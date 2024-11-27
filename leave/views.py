from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LeaveRequest
from accounts.models import Employee
from .serializers import LeaveRequestSerializer
from datetime import datetime
from notifications.tasks import send_notification
from django.http import HttpResponse
from notifications.models import Notification
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Leave Management']

    @swagger_auto_schema(
        operation_description="List all leave requests. For admin users, shows all requests. For regular users, shows only their requests.",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by leave request status",
                type=openapi.TYPE_STRING,
                enum=['pending', 'approved', 'rejected']
            ),
        ],
        responses={
            200: LeaveRequestSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new leave request",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['start_date', 'end_date', 'reason'],
            properties={
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'reason': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            201: LeaveRequestSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific leave request",
        responses={
            200: LeaveRequestSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a leave request",
        request_body=LeaveRequestSerializer,
        responses={
            200: LeaveRequestSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a leave request",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_admin:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee=self.request.user)

@login_required
def leave_list(request):
    if request.user.is_admin:
        leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    else:
        leave_requests = LeaveRequest.objects.filter(
            employee=request.user
        ).order_by('-created_at')
    
    return render(request, 'leave/leave_list.html', {'leave_requests': leave_requests})

@login_required
def leave_request(request):
    if request.method == 'POST':
        LeaveRequest.objects.create(
            employee=request.user,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            reason=request.POST.get('reason')
        )
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave:leave_list')
    return render(request, 'leave/leave_request.html')

@login_required
def approve_leave(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('leave:leave_list')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    remaining_days = leave_request.employee.remaining_leave_days
    leave_days = (leave_request.end_date - leave_request.start_date).days + 1
    
    if remaining_days is not None and remaining_days < leave_days:
        messages.error(request, 'Employee does not have enough leave days.')
        return redirect('leave:leave_list')
    
    leave_request.status = 'approved'
    leave_request.employee.used_leave_days += leave_days
    
    leave_request.save()
    leave_request.employee.save()
    
    if leave_request.employee.remaining_leave_days < 3:
        from notifications.tasks import should_send_low_balance_notification
        if should_send_low_balance_notification(leave_request.employee):
            admins = Employee.objects.filter(is_admin=True)
            for admin in admins:
                send_notification.delay(
                    admin.id,
                    'Low Leave Balance Alert',
                    f"Low leave balance alert: {leave_request.employee.get_full_name()} has {leave_request.employee.remaining_leave_days:.1f} days remaining"
                )
    
    messages.success(request, f'Leave request approved. {leave_days} days deducted from annual leave.')
    return redirect('leave:leave_list')

@login_required
def reject_leave(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('leave:leave_list')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    leave_request.status = 'rejected'
    leave_request.save()
    messages.success(request, 'Leave request rejected.')
    return redirect('leave:leave_list')

@login_required
def request_leave(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        # Validate dates
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start > end:
            messages.error(request, 'Start date cannot be after end date')
            return redirect('leave:request')
        
        # Calculate required leave days
        leave_days = (end - start).days + 1
        
        if request.user.remaining_leave_days < leave_days:
            messages.error(request, f'Not enough leave days. You need {leave_days} days but only have {request.user.remaining_leave_days} remaining.')
            return redirect('leave:request')
        
        LeaveRequest.objects.create(
            employee=request.user,
            start_date=start,
            end_date=end,
            reason=reason
        )
        
        messages.success(request, 'Leave request submitted successfully')
        return redirect('leave:leave_list')
        
    return render(request, 'leave/leave_request.html')
