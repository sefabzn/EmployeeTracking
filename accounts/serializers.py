from rest_framework import serializers
from .models import Employee, LeavePermission

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'email', 'first_name', 'last_name', 'is_admin', 'remaining_leave_days']
        read_only_fields = ['remaining_leave_days']

class LeavePermissionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = LeavePermission
        fields = [
            'id', 'employee', 'employee_name', 'max_leaves_per_year',
            'can_carry_forward', 'max_carry_forward_days',
            'min_days_before_request', 'requires_approval'
        ]