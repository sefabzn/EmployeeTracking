from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('late_checkin', 'Late Check-in'),
        ('leave_reminder', 'Leave Reminder'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES,
        default='late_checkin'
    )

    class Meta:
        ordering = ['-created_at']
