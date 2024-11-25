from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, AttendanceNotification
from .serializers import AttendanceSerializer
from datetime import time
from notifications.tasks import send_notification
from django.contrib.auth import get_user_model
from django.db.models import Q
from notifications.models import Notification
from accounts.models import Employee
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Attendance.objects.all()
        return Attendance.objects.filter(employee=self.request.user)

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        today = timezone.now().date()
        if Attendance.objects.filter(employee=request.user, date=today).exists():
            return Response(
                {'error': 'You can only check in once per day'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendance = Attendance.objects.create(
            employee=request.user,
            date=today,
            check_in=timezone.now().time()
        )
        return Response({'message': 'Check-in successful'})

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        today = timezone.now().date()
        try:
            attendance = Attendance.objects.get(
                employee=request.user,
                date=today,
                check_out__isnull=True
            )
            if attendance.check_out:
                return Response(
                    {'error': 'You can only check out once per day'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            attendance.check_out = timezone.now().time()
            attendance.save()
            return Response({'message': 'Check-out successful'})
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'No active check-in found for today'},
                status=status.HTTP_400_BAD_REQUEST
            )

@login_required
def attendance_request(request):
    if request.method == 'POST':
        try:
            # Get current time in the correct timezone
            current_time = timezone.now()
            
            # Create attendance record
            attendance = Attendance.objects.create(
                employee=request.user,
                check_in=current_time,
                date=current_time.date()
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Check-in recorded successfully',
                'time': current_time.strftime('%H:%M:%S')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    elif request.method == 'GET':
        # Get today's attendance for the user
        today = timezone.now().date()
        attendance = Attendance.objects.filter(
            employee=request.user,
            date=today
        ).first()
        
        return JsonResponse({
            'status': 'success',
            'has_checked_in': attendance is not None,
            'check_in_time': attendance.check_in.strftime('%H:%M:%S') if attendance else None,
            'check_out_time': attendance.check_out.strftime('%H:%M:%S') if attendance and attendance.check_out else None
        })

@login_required
def check_out(request):
    if request.method == 'POST':
        try:
            current_time = timezone.now()
            today = current_time.date()
            
            attendance = Attendance.objects.filter(
                employee=request.user,
                date=today,
                check_out__isnull=True
            ).first()
            
            if attendance:
                attendance.check_out = current_time
                attendance.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Check-out recorded successfully',
                    'time': current_time.strftime('%H:%M:%S')
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No active check-in found for today'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

def is_admin(user):
    return user.is_admin

@login_required
@user_passes_test(is_admin)
def attendance_list(request):
    if request.user.is_admin:
        attendances = Attendance.objects.all().order_by('-date')
    else:
        attendances = Attendance.objects.filter(employee=request.user).order_by('-date')
        
    ideal_check_in = time(8, 0)  # 8:00 AM
    #attendance status
    for attendance in attendances:
        if attendance.check_in:
            check_in_time = attendance.check_in
            minutes_diff = (check_in_time.hour * 60 + check_in_time.minute) - (ideal_check_in.hour * 60)
            
            hours = abs(minutes_diff) // 60
            minutes = abs(minutes_diff) % 60
            
            if minutes_diff > 0:
                if hours > 0:
                    attendance.status = f"Late by {hours}h {minutes}m"
                else:
                    attendance.status = f"Late by {minutes}m"
            else:
                if hours > 0:
                    attendance.status = f"Early by {hours}h {minutes}m"
                else:
                    attendance.status = f"Early by {minutes}m"
        else:
            attendance.status = "No check-in"
    
    context = {
        'attendances': attendances,
        'ideal_check_in': ideal_check_in
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    notifications = AttendanceNotification.objects.all().order_by('-created_at')[:10]
    return render(request, 'attendance/admin_notifications.html', {'notifications': notifications})

@login_required
def all_notifications(request):
    if request.user.is_admin:
        # Create leave reminder notifications
        employees_low_leave = Employee.objects.filter(
            annual_leave_days__gt=0
        ).exclude(is_admin=True)

        for employee in employees_low_leave:
            remaining_days = employee.remaining_leave_days
            if remaining_days <= 3:
                Notification.objects.get_or_create(
                    recipient=request.user,
                    message=f"{employee.get_full_name()} has {remaining_days} leave days remaining",
                    notification_type='leave_reminder',
                    defaults={'is_read': False}
                )

        # Get all notifications (both types)
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')
    else:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')

    context = {
        'notifications': notifications,
        'title': 'All Notifications'
    }
    return render(request, 'attendance/notifications.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin)
def monthly_summary(request):
    # Get the current month and year
    today = timezone.now()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Get all employees
    employees = Employee.objects.filter(is_admin=False)
    
    # Calculate monthly statistics for each employee
    monthly_stats = []
    start_time = time(8, 0)  # 8:00 AM
    
    for employee in employees:
        # Get attendance records for the specified month
        attendances = Attendance.objects.filter(
            employee=employee,
            date__month=month,
            date__year=year,
            check_out__isnull=False
        )
        
        # Calculate total working hours
        total_hours = 0
        for attendance in attendances:
            if attendance.check_out:
                # Convert time objects to datetime for calculation
                today = attendance.date
                check_in_dt = timezone.make_aware(datetime.combine(today, attendance.check_in))
                check_out_dt = timezone.make_aware(datetime.combine(today, attendance.check_out))
                duration = check_out_dt - check_in_dt
                total_hours += duration.total_seconds() / 3600
        
        # Calculate average daily hours
        working_days = attendances.count()
        avg_daily_hours = round(total_hours / working_days, 2) if working_days > 0 else 0
        
        # Calculate late check-ins
        late_check_ins = attendances.filter(
            check_in__gt=start_time
        ).count()
        
        monthly_stats.append({
            'employee': employee,
            'total_hours': round(total_hours, 2),
            'working_days': working_days,
            'avg_daily_hours': avg_daily_hours,
            'late_check_ins': late_check_ins
        })
    
    context = {
        'monthly_stats': monthly_stats,
        'current_month': datetime(year, month, 1).strftime('%B %Y'),
        'month': month,
        'year': year
    }
    
    return render(request, 'attendance/monthly_summary.html', context)
