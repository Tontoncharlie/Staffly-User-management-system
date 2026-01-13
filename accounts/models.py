"""
Custom User Model for Staffly.
Uses email as the primary identifier with role-based access control.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    Includes role-based access control with ADMIN, STAFF, and USER roles.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        STAFF = 'STAFF', 'Staff Member'
        USER = 'USER', 'Regular User'
    
    # Primary fields
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.',
        }
    )
    first_name = models.CharField('first name', max_length=150, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    
    # Role and status
    role = models.CharField(
        'role',
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        help_text='User role determines access level in the system.'
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into the admin site.'
    )
    
    # Profile fields
    phone = models.CharField('phone number', max_length=20, blank=True)
    department = models.CharField('department', max_length=100, blank=True)
    job_title = models.CharField('job title', max_length=100, blank=True)
    profile_picture = models.ImageField(
        'profile picture',
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    bio = models.TextField('bio', max_length=500, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    last_login = models.DateTimeField('last login', blank=True, null=True)
    updated_at = models.DateTimeField('last updated', auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & password are required by default
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name if self.first_name else self.email.split('@')[0]
    
    def get_initials(self):
        """Return user initials for avatar display."""
        if self.first_name and self.last_name:
            return f'{self.first_name[0]}{self.last_name[0]}'.upper()
        elif self.first_name:
            return self.first_name[:2].upper()
        return self.email[:2].upper()
    
    # Role check methods
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN
    
    def is_staff_member(self):
        """Check if user has staff role."""
        return self.role == self.Role.STAFF
    
    def is_regular_user(self):
        """Check if user has regular user role."""
        return self.role == self.Role.USER
    
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role == self.Role.ADMIN
    
    def can_view_analytics(self):
        """Check if user can view system analytics."""
        return self.role == self.Role.ADMIN
    
    def can_access_staff_features(self):
        """Check if user can access staff features."""
        return self.role in [self.Role.ADMIN, self.Role.STAFF]
