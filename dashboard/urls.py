"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_router, name='router'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('staff/', views.staff_dashboard, name='staff'),
    path('user/', views.user_dashboard, name='user'),
]
