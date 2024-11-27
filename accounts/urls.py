from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('employee-permissions/', views.employee_permissions, name='employee_permissions'),
]
