from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance
from leave.models import LeaveRequest
from notifications.models import Notification
from django.utils import timezone
from datetime import timedelta

@login_required
def home(request):
    context = {
        'annual_leave': request.user.annual_leave_days,
        'remaining_leave': request.user.remaining_leave_days,
        'used_leave': request.user.used_leave_days,
    }

    if request.user.is_admin:
        # Get the last 10 late check-ins from notifications
        late_checkins = Notification.objects.filter(
            notification_type='late_checkin'
        ).order_by('-created_at')[:10]

        # Get the last 10 leave requests
        leave_requests = LeaveRequest.objects.all().order_by('-created_at')[:10]

        # Combine both types of activities
        activities = []

        # Add late check-ins to activities
        for checkin in late_checkins:
            activities.append({
                'type': 'late_checkin',
                'message': checkin.message,
                'date': checkin.created_at,
                'status': None
            })

        # Add leave requests to activities
        for leave in leave_requests:
            activities.append({
                'type': 'leave_request',
                'message': f"{leave.employee.get_full_name()} requested leave",
                'date': leave.created_at,
                'status': leave.status
            })

        # Sort all activities by date, most recent first
        activities.sort(key=lambda x: x['date'], reverse=True)
        activities = activities[:10]

        # Update context with admin specific data
        context.update({
            'activities': activities,
            'active_tab': 'employee-tracking'
        })

    return render(request, 'core/home.html', context)
