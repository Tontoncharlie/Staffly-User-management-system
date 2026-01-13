"""
Django Admin configuration for Staffly accounts app.
Provides a customized admin interface for user management.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.
    """
    
    # List display
    list_display = (
        'email', 
        'full_name', 
        'role_badge', 
        'status_badge', 
        'department',
        'date_joined',
        'last_login',
    )
    
    list_filter = (
        'role', 
        'is_active', 
        'is_staff', 
        'is_superuser',
        'date_joined',
        'department',
    )
    
    search_fields = (
        'email', 
        'first_name', 
        'last_name', 
        'department',
        'job_title',
    )
    
    ordering = ('-date_joined',)
    
    # Fieldsets for add/edit forms
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'bio', 'profile_picture')
        }),
        ('Work Information', {
            'fields': ('department', 'job_title')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    # Custom methods for list display
    def full_name(self, obj):
        """Display user's full name."""
        return obj.get_full_name() or '-'
    full_name.short_description = 'Name'
    
    def role_badge(self, obj):
        """Display role as a colored badge."""
        colors = {
            'ADMIN': '#dc2626',    # Red
            'STAFF': '#2563eb',    # Blue
            'USER': '#16a34a',     # Green
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #16a34a; color: white; padding: 3px 8px; '
                'border-radius: 4px; font-size: 11px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc2626; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">Inactive</span>'
        )
    status_badge.short_description = 'Status'
    
    # Admin actions
    actions = ['activate_users', 'deactivate_users', 'make_staff', 'make_regular_user']
    
    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) activated.')
    
    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        # Don't deactivate the current user
        queryset = queryset.exclude(pk=request.user.pk)
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) deactivated.')
    
    @admin.action(description='Change role to Staff')
    def make_staff(self, request, queryset):
        count = queryset.update(role='STAFF')
        self.message_user(request, f'{count} user(s) changed to Staff role.')
    
    @admin.action(description='Change role to Regular User')
    def make_regular_user(self, request, queryset):
        # Don't change the current user's role
        queryset = queryset.exclude(pk=request.user.pk)
        count = queryset.update(role='USER')
        self.message_user(request, f'{count} user(s) changed to Regular User role.')
