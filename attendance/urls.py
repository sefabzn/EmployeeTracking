from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('request/', views.attendance_request, name='request'),
    path('list/', views.attendance_list, name='attendance_list'),
    path('notifications/', views.all_notifications, name='notifications'),
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
]
