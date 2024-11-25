from .models import AttendanceNotification

def notifications(request):
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
    
    if request.user.is_authenticated and request.user.is_admin:
        context['unread_notifications_count'] = AttendanceNotification.objects.filter(
            employee=request.user,
            is_read=False
        ).count()
        context['recent_notifications'] = AttendanceNotification.objects.filter(
            employee=request.user
        ).order_by('-created_at')[:5]
    
    return context 