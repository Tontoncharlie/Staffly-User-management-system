"""
Middleware for Staffly.
Handles role-based access control at the middleware level.
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class RoleBasedAccessMiddleware:
    """
    Middleware that enforces role-based access control.
    Checks if users have appropriate roles for protected URL patterns.
    """
    
    # URL patterns that require admin role
    ADMIN_ONLY_PATTERNS = [
        '/users/',
        '/users/create/',
        '/users/delete/',
        '/analytics/',
    ]
    
    # URL patterns that require staff or admin role
    STAFF_PATTERNS = [
        '/staff/',
    ]
    
    # URLs that should be accessible without authentication
    PUBLIC_PATTERNS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/static/',
        '/media/',
        '/admin/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip middleware for public patterns
        for pattern in self.PUBLIC_PATTERNS:
            if request.path.startswith(pattern):
                return self.get_response(request)
        
        # Skip if user is not authenticated (let login_required handle it)
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check admin-only patterns
        for pattern in self.ADMIN_ONLY_PATTERNS:
            if request.path.startswith(pattern):
                if request.user.role != 'ADMIN':
                    messages.error(request, 'Administrator access required.')
                    return redirect('dashboard:router')
        
        # Check staff patterns
        for pattern in self.STAFF_PATTERNS:
            if request.path.startswith(pattern):
                if request.user.role not in ['ADMIN', 'STAFF']:
                    messages.error(request, 'Staff access required.')
                    return redirect('dashboard:router')
        
        return self.get_response(request)


class UpdateLastLoginMiddleware:
    """
    Middleware that updates the user's last login timestamp
    on each request (rate limited to once per hour).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            from django.utils import timezone
            from datetime import timedelta
            
            # Update last login if more than 1 hour has passed
            if request.user.last_login:
                time_since_login = timezone.now() - request.user.last_login
                if time_since_login > timedelta(hours=1):
                    request.user.last_login = timezone.now()
                    request.user.save(update_fields=['last_login'])
            else:
                request.user.last_login = timezone.now()
                request.user.save(update_fields=['last_login'])
        
        return self.get_response(request)
