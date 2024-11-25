from rest_framework import serializers
from .models import LeaveRequest

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'start_date', 'end_date', 'reason', 'status', 'created_at']
        read_only_fields = ['employee', 'status']

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)
