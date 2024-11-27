from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer
from datetime import time
from notifications.tasks import send_notification
from django.contrib.auth import get_user_model
from django.db.models import Q
from notifications.models import Notification
from django.http import JsonResponse
from datetime import datetime
from calendar import monthrange
from django.db.models import Sum, F
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Attendance']

    @swagger_auto_schema(
        operation_description="List all attendance records",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Filter by date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date'
            ),
        ],
        responses={
            200: AttendanceSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Record check-in for the current day",
        responses={
            200: openapi.Response(
                description="Check-in successful",
                examples={
                    "application/json": {
                        "message": "Check-in successful"
                    }
                }
            ),
            400: "Already checked in or invalid request",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        return super().check_in(request)

    @swagger_auto_schema(
        operation_description="Record check-out for the current day",
        responses={
            200: openapi.Response(
                description="Check-out successful",
                examples={
                    "application/json": {
                        "message": "Check-out successful"
                    }
                }
            ),
            400: "No active check-in or already checked out",
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        return super().check_out(request)

@login_required
def attendance_request(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        current_time = timezone.now().time()
        today = timezone.now().date()
        
        if action == 'check_in':
            attendance = Attendance.objects.filter(
                employee=request.user,
                date=today
            ).first()
            
            if attendance and attendance.check_in:
                messages.error(request, 'Already checked in today')
                return redirect('attendance:request')
            
            if not attendance:
                attendance = Attendance.objects.create(
                    employee=request.user,
                    date=today,
                    check_in=current_time
                )
            else:
                attendance.check_in = current_time
                attendance.save()
            
            messages.success(request, 'Check-in successful')
            
        elif action == 'check_out':
            try:
                attendance = Attendance.objects.get(
                    employee=request.user,
                    date=today,
                    check_out__isnull=True
                )
                attendance.check_out = current_time
                attendance.save()
                messages.success(request, 'Check-out successful')
            except Attendance.DoesNotExist:
                messages.error(request, 'No active check-in found')
        
        return redirect('attendance:request')
    
    return render(request, 'attendance/attendance_request.html', {
        'is_checked_in': Attendance.objects.filter(
            employee=request.user,
            date=timezone.now().date(),
            check_out__isnull=True
        ).exists()
    })

def is_admin(user):
    return user.is_admin

@login_required
@user_passes_test(is_admin)
def attendance_list(request):
    if request.user.is_admin:
        attendances = Attendance.objects.all().order_by('-date')
    else:
        attendances = Attendance.objects.filter(employee=request.user).order_by('-date')
    
    # Add computed properties for template
    for attendance in attendances:
        attendance.first_check_in = attendance.check_in
        attendance.last_check_out = attendance.check_out
        attendance.check_in_count = 1 if attendance.check_in else 0
        attendance.check_out_count = 1 if attendance.check_out else 0
    
    context = {
        'attendances': attendances,
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
        notification_type__in=['late_checkin', 'missing_checkout', 'absent']
    ).order_by('-created_at')[:10]
    return render(request, 'attendance/admin_notifications.html', {'notifications': notifications})

@login_required
def all_notifications(request):
    if request.user.is_admin:
        # Admin sees all notifications
        notifications = Notification.objects.all()
    else:
        # Regular users see only their notifications
        notifications = Notification.objects.filter(recipient=request.user)
    
    notifications = notifications.order_by('-created_at')
    
    context = {
        'notifications': notifications,
        'title': 'All Notifications'
    }
    return render(request, 'attendance/notifications.html', context)

@login_required
@user_passes_test(is_admin)
def monthly_summary(request):
    # Get the month and year from query parameters or use current date
    today = timezone.now()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Get all attendance records for the specified month
    User = get_user_model()
    employees = User.objects.filter(is_active=True)
    
    # Calculate working hours for each employee
    summary_data = []
    for employee in employees:
        attendances = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )
        
        total_hours = attendances.aggregate(
            total=Sum(F('check_out') - F('check_in'))
        )['total']
        
        if total_hours:
            total_hours = total_hours.total_seconds() / 3600  # Convert to hours
        else:
            total_hours = 0
            
        summary_data.append({
            'employee': employee,
            'total_hours': round(total_hours, 2)
        })
    
    context = {
        'summary_data': summary_data,
        'current_month': datetime(year, month, 1).strftime('%B %Y'),
        'month': month,
        'year': year
    }
    
    return render(request, 'attendance/monthly_summary.html', context)


