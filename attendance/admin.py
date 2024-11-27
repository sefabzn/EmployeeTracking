from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'late_minutes', 'work_hours')
    list_filter = ('date', 'employee')
    search_fields = ('employee__email', 'employee__first_name', 'employee__last_name')
