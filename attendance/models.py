from django.db import models
from django.conf import settings
from django.utils import timezone

class Attendance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0)
    
    @property
    def working_hours(self):
        if self.check_out:
            duration = self.check_out - self.check_in
            return round(duration.total_seconds() / 3600, 2)
        return 0

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date}"

class AttendanceNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('late_checkin', 'Late Check-in'),
        ('missing_checkout', 'Missing Check-out'),
        ('absent', 'Absent'),
    )

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.notification_type} - {self.created_at.date()}"
