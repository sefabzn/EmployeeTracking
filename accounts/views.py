from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer
from notifications.models import Notification

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('core:home')
        return redirect('core:home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None and not user.is_admin:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('core:home')
        return redirect('core:home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_admin:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid admin credentials.')
    
    return render(request, 'accounts/admin_login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('accounts:login')

@login_required
def admin_logout(request):
    if not request.user.is_admin:
        return redirect('accounts:login')
    logout(request)
    messages.success(request, 'Admin successfully logged out.')
    return redirect('accounts:admin_login')

@login_required
def profile(request):
    context = {
        'user': request.user,
        'annual_leave': request.user.annual_leave_days,
        'used_leave': request.user.used_leave_days,
        'remaining_leave': request.user.remaining_leave_days
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('accounts:login')

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Employee.objects.all()
        return Employee.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def datatable(self, request):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')

        # Initial queryset
        queryset = self.get_queryset()

        # Search
        if search_value:
            queryset = queryset.filter(
                Q(first_name__icontains=search_value) |
                Q(last_name__icontains=search_value) |
                Q(email__icontains=search_value)
            )

        # Total records
        total_records = queryset.count()

        # Ordering
        order_column = request.GET.get('order[0][column]', 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')
        columns = ['first_name', 'last_name', 'email', 'remaining_leave_days']
        
        if order_column and int(order_column) < len(columns):
            column = columns[int(order_column)]
            if order_dir == 'desc':
                column = f'-{column}'
            queryset = queryset.order_by(column)

        # Pagination
        queryset = queryset[start:start + length]

        # Serialize data
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def notifications(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')
        
        return Response({
            'notifications': [{
                'id': notif.id,
                'message': notif.message,
                'timestamp': notif.created_at,
                'is_read': notif.is_read,
                'notification_type': notif.notification_type
            } for notif in notifications]
        })

    @action(detail=False, methods=['post'])
    def mark_notification_read(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({'status': 'success'})
        except Notification.DoesNotExist:
            return Response({'status': 'error', 'message': 'Notification not found'}, status=404)
