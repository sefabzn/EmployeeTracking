from notifications.models import Notification

def notifications(request):
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
    
    if request.user.is_authenticated:
        context['unread_notifications_count'] = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        context['recent_notifications'] = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
    
    return context 