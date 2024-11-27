from django.urls import path, include
from django.contrib import admin
from rest_framework import routers
from leave.views import LeaveRequestViewSet
from attendance.views import AttendanceViewSet
from accounts.views import EmployeeViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Create a router and register viewsets
router = routers.DefaultRouter()
router.register('leave', LeaveRequestViewSet, basename='leave')
router.register('attendance', AttendanceViewSet, basename='attendance')
router.register('employees', EmployeeViewSet, basename='employee')

# Schema view configuration AFTER router is configured
schema_view = get_schema_view(
    openapi.Info(
        title="Employee Tracking API",
        default_version='v1',
        description="API documentation for Employee Tracking System",
        contact=openapi.Contact(email="contact@employeetracking.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include(router.urls)),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('leave/', include('leave.urls')),
    path('attendance/', include('attendance.urls')),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]