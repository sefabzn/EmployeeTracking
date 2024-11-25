from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee

class EmployeeAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'annual_leave_days', 'used_leave_days')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('used_leave_days',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'annual_leave_days')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'annual_leave_days', 'is_admin', 'is_active'),
        }),
    )
    
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Employee, EmployeeAdmin)
