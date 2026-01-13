"""
Core context processors for Staffly.
Provides global template context variables.
"""


def user_role_context(request):
    """
    Add user role information to template context.
    This makes role information available in all templates.
    """
    context = {
        'is_admin': False,
        'is_staff_member': False,
        'is_regular_user': False,
        'user_role': None,
        'user_role_display': 'Guest',
    }
    
    if request.user.is_authenticated:
        user = request.user
        context['user_role'] = user.role
        context['user_role_display'] = user.get_role_display()
        
        if user.role == 'ADMIN':
            context['is_admin'] = True
        elif user.role == 'STAFF':
            context['is_staff_member'] = True
        else:
            context['is_regular_user'] = True
    
    return context
