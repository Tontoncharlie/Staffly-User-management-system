"""
Dashboard views for Staffly.
Provides role-based dashboards for Admin, Staff, and Regular users.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from accounts.decorators import admin_required, staff_required


@login_required
def dashboard_router(request):
    """
    Route users to their appropriate dashboard based on role.
    """
    user = request.user
    
    if user.role == 'ADMIN':
        return redirect('dashboard:admin')
    elif user.role == 'STAFF':
        return redirect('dashboard:staff')
    else:
        return redirect('dashboard:user')


@admin_required
def admin_dashboard(request):
    """
    Admin dashboard with system analytics and user statistics.
    """
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    # Role breakdown
    admin_count = User.objects.filter(role='ADMIN').count()
    staff_count = User.objects.filter(role='STAFF').count()
    user_count = User.objects.filter(role='USER').count()
    
    # Recent activity
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Active today (logged in today)
    active_today = User.objects.filter(last_login__date=today).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_count': admin_count,
        'staff_count': staff_count,
        'user_count': user_count,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'recent_users': recent_users,
        'active_today': active_today,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@staff_required
def staff_dashboard(request):
    """
    Staff dashboard with limited view.
    """
    # Staff can see other staff and regular users
    colleagues = User.objects.filter(
        role__in=['STAFF', 'USER'],
        is_active=True
    ).exclude(pk=request.user.pk).order_by('first_name')[:10]
    
    # Department members
    if request.user.department:
        department_members = User.objects.filter(
            department=request.user.department,
            is_active=True
        ).exclude(pk=request.user.pk)
    else:
        department_members = User.objects.none()
    
    context = {
        'colleagues': colleagues,
        'department_members': department_members,
    }
    
    return render(request, 'dashboard/staff_dashboard.html', context)


@login_required
def user_dashboard(request):
    """
    Regular user dashboard with personal information.
    """
    context = {
        'user': request.user,
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)
