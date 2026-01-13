"""
Permission decorators for Staffly.
Provides role-based access control for views.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """
    Decorator that checks if user has one of the allowed roles.
    
    Usage:
        @role_required(['ADMIN', 'STAFF'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:router')
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator that ensures only admin users can access the view.
    
    Usage:
        @admin_required
        def admin_only_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Administrator access required.')
        return redirect('dashboard:router')
    return wrapper


def staff_required(view_func):
    """
    Decorator that ensures only staff or admin users can access the view.
    
    Usage:
        @staff_required
        def staff_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role in ['ADMIN', 'STAFF']:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Staff access required.')
        return redirect('dashboard:router')
    return wrapper


def user_required(view_func):
    """
    Decorator that ensures any authenticated user can access the view.
    Essentially the same as login_required but with consistent messaging.
    
    Usage:
        @user_required
        def user_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper


def anonymous_required(view_func):
    """
    Decorator that ensures only anonymous (not logged in) users can access.
    Useful for login and registration pages.
    
    Usage:
        @anonymous_required
        def login_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:router')
        return view_func(request, *args, **kwargs)
    return wrapper


class RoleRequiredMixin:
    """
    Mixin for class-based views that require specific roles.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['ADMIN', 'STAFF']
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if request.user.role not in self.allowed_roles:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:router')
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin that requires admin role."""
    allowed_roles = ['ADMIN']


class StaffRequiredMixin(RoleRequiredMixin):
    """Mixin that requires staff or admin role."""
    allowed_roles = ['ADMIN', 'STAFF']
