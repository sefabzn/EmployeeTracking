from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import Employee
from attendance.models import Attendance
from leave.models import LeaveRequest
from django.contrib.auth import get_user_model
from attendance.models import AttendanceNotification

@shared_task
def send_notification(user_id, title, message):
    # Create notification in database
    notification = Notification.objects.create(
        recipient_id=user_id,
        title=title,
        message=message
    )

    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notification_message",
            "message": {
                "title": title,
                "message": message
            }
        }
    )
    return notification.id

@shared_task
def check_late_arrivals():
    today = timezone.now().date()
    work_start = timezone.datetime.strptime('08:00', '%H:%M').time()
    
    late_attendances = Attendance.objects.filter(
        date=today,
        check_in__gt=work_start
    ).select_related('employee')
    
    for attendance in late_attendances:
        # Calculate minutes late
        time_diff = datetime.combine(today, attendance.check_in) - datetime.combine(today, work_start)
        minutes_late = time_diff.seconds // 60
        
        # Send notification to employee
        send_notification.delay(
            attendance.employee.id,
            'Late Arrival Notice',
            f'You arrived {minutes_late} minutes late today.'
        )
        
        # Send notification to admin
        admin_users = Employee.objects.filter(is_admin=True)
        for admin in admin_users:
            send_notification.delay(
                admin.id,
                'Employee Late Arrival',
                f'{attendance.employee.get_full_name()} arrived {minutes_late} minutes late today.'
            )

@shared_task
def check_leave_balance():
    Employee = get_user_model()
    employees = Employee.objects.filter(
        is_admin=False,  # Only check non-admin employees
        annual_leave_days__gt=0,  # Only check employees with leave balance
        used_leave_days__gt=0  # Only check employees who have used leave
    )
    
    for employee in employees:
        remaining_days = employee.remaining_leave_days
        if remaining_days is not None and remaining_days < 3:
            # Get all admin users
            admins = Employee.objects.filter(is_admin=True)
            
            # Create notification for each admin
            for admin in admins:
                AttendanceNotification.objects.create(
                    employee=admin,
                    message=f"Low leave balance alert: {employee.get_full_name()} has {remaining_days:.1f} days remaining"
                )

@shared_task
def generate_monthly_report():
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    employees = Employee.objects.all()
    for employee in employees:
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        )
        
        # Calculate statistics
        total_days = attendance_records.count()
        late_days = attendance_records.filter(late_minutes__gt=0).count()
        total_work_hours = sum(
            (a.check_out.hour * 60 + a.check_out.minute) - 
            (a.check_in.hour * 60 + a.check_in.minute)
            for a in attendance_records if a.check_in and a.check_out
        ) / 60
        
        # Get leave requests
        leave_requests = LeaveRequest.objects.filter(
            employee=employee,
            start_date__gte=start_date,
            end_date__lte=end_date,
            status='approved'
        ).count()
        
        # Generate report message
        report_message = f"""Monthly Attendance Report ({start_date} to {end_date})
        - Total Working Days: {total_days}
        - Late Arrivals: {late_days}
        - Total Work Hours: {total_work_hours:.2f}
        - Leave Days Taken: {leave_requests}
        - Remaining Leave Balance: {employee.remaining_leave_days}
        """
        
        # Send report to employee
        send_notification.delay(
            employee.id,
            'Monthly Attendance Report',
            report_message
        )
