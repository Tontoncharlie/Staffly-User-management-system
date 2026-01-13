"""
Views for Staffly accounts app.
Handles authentication and user management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from .models import User
from .forms import (
    LoginForm, 
    UserCreationForm, 
    UserUpdateForm, 
    AdminUserUpdateForm,
    PasswordChangeForm
)
from .decorators import admin_required, anonymous_required


# ============================================================================
# Authentication Views
# ============================================================================

@anonymous_required
def login_view(request):
    """
    Handle user login with role-based redirect.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Session expires when browser closes
            
            messages.success(request, f'Welcome back, {user.get_short_name()}!')
            
            # Redirect to next URL or dashboard
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:router')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ============================================================================
# User Management Views (Admin Only)
# ============================================================================

@admin_required
def user_list(request):
    """
    Display paginated list of all users with filtering.
    Admin only.
    """
    users = User.objects.all()
    
    # Search filter
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(department__icontains=search)
        )
    
    # Role filter
    role = request.GET.get('role', '')
    if role:
        users = users.filter(role=role)
    
    # Status filter
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Ordering
    ordering = request.GET.get('ordering', '-date_joined')
    users = users.order_by(ordering)
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'role': role,
        'status': status,
        'ordering': ordering,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'roles': User.Role.choices,
    }
    
    return render(request, 'accounts/user_list.html', context)


@admin_required
def user_create(request):
    """
    Create a new user.
    Admin only.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.email} created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create New User',
        'submit_text': 'Create User',
    })


@admin_required
def user_detail(request, pk):
    """
    View user details.
    Admin only.
    """
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user_obj': user})


@admin_required
def user_update(request, pk):
    """
    Update any user's information.
    Admin only.
    """
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.email} updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = AdminUserUpdateForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit User: {user.email}',
        'submit_text': 'Save Changes',
        'user_obj': user,
    })


@admin_required
@require_POST
def user_delete(request, pk):
    """
    Delete a user.
    Admin only.
    """
    user = get_object_or_404(User, pk=pk)
    
    # Prevent self-deletion
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:user_list')
    
    email = user.email
    user.delete()
    messages.success(request, f'User {email} deleted successfully.')
    return redirect('accounts:user_list')


@admin_required
@require_POST
def user_toggle_status(request, pk):
    """
    Toggle user active/inactive status.
    Admin only.
    """
    user = get_object_or_404(User, pk=pk)
    
    # Prevent self-deactivation
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('accounts:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.email} has been {status}.')
    return redirect('accounts:user_list')


# ============================================================================
# Profile Views
# ============================================================================

@login_required
def profile_view(request):
    """
    View current user's profile.
    """
    return render(request, 'accounts/profile.html', {'user_obj': request.user})


@login_required
def profile_update(request):
    """
    Update current user's profile.
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {
        'form': form,
    })


@login_required
def password_change(request):
    """
    Change current user's password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {
        'form': form,
    })
