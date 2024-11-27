from django.urls import path
from . import views

app_name = 'leave'

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('request/', views.request_leave, name='request'),
    path('approve/<int:pk>/', views.approve_leave, name='approve'),
    path('reject/<int:pk>/', views.reject_leave, name='reject'),
]
