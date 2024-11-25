from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LeaveRequestViewSet

app_name = 'leave'

router = DefaultRouter()
router.register('api', LeaveRequestViewSet, basename='leave')

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('request/', views.request_leave, name='request'),
    path('approve/<int:pk>/', views.approve_leave, name='approve'),
    path('reject/<int:pk>/', views.reject_leave, name='reject'),
    path('api/', include(router.urls)),
]
