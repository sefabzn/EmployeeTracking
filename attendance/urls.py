from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('request/', views.attendance_request, name='request'),
    path('notifications/', views.all_notifications, name='notifications'),
    path('admin-notifications/', views.admin_notifications, name='admin_notifications'),
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
]
