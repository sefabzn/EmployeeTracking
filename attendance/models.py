from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time

class Attendance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True)
    late_minutes = models.IntegerField(default=0)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    WORK_START_TIME = time(8, 0)  # 8:00 AM
    WORK_END_TIME = time(18, 0)   # 6:00 PM
    
    class Meta:
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        if self.check_in:
            # Calculate late minutes
            work_start = datetime.combine(self.date, self.WORK_START_TIME)
            check_in_datetime = datetime.combine(self.date, self.check_in)
            
            if check_in_datetime > work_start:
                td = check_in_datetime - work_start
                self.late_minutes = td.seconds // 60
            
            # Calculate work hours if check-out exists
            if self.check_out:
                check_out_datetime = datetime.combine(self.date, self.check_out)
                td = check_out_datetime - check_in_datetime
                self.work_hours = round(td.seconds / 3600, 2)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee} - {self.date}"

