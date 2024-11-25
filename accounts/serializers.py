from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'email', 'first_name', 'last_name', 'is_admin', 'remaining_leave_days']
        read_only_fields = ['remaining_leave_days']
