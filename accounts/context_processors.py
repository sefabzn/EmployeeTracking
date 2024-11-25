from notifications.models import Notification
from django.db.models import Q

def notification_processor(request):
    if request.user.is_authenticated and request.user.is_admin:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')

        unread_count = notifications.filter(is_read=False).count()
        recent_notifications = notifications[:5]

        return {
            'recent_notifications': recent_notifications,
            'unread_notifications_count': unread_count,
        }
    return {
        'recent_notifications': [],
        'unread_notifications_count': 0,
    } 