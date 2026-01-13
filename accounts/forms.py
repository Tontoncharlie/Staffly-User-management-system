"""
Forms for Staffly accounts app.
Handles user authentication, creation, and profile management.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User


class LoginForm(forms.Form):
    """
    Custom login form using email instead of username.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'autofocus': True,
        }),
        label='Email Address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
        }),
        label='Password'
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
        }),
        label='Remember me'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError('Invalid email or password.')
            if not user.is_active:
                raise ValidationError('This account has been deactivated.')
            cleaned_data['user'] = user
        
        return cleaned_data


class UserCreationForm(forms.ModelForm):
    """
    Form for creating new users (Admin only).
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password',
        }),
        help_text='Password must be at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password',
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'department', 'job_title', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'user@company.com',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name',
            }),
            'role': forms.Select(attrs={
                'class': 'form-select',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Engineering',
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Software Developer',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for users to update their own profile.
    Limited fields - users cannot change their role or status.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'department', 'job_title', 'bio', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1 234 567 8900',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Department',
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Job title',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us about yourself...',
                'rows': 4,
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
        }


class AdminUserUpdateForm(forms.ModelForm):
    """
    Form for admins to update any user.
    Includes role and status fields.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active', 
                  'phone', 'department', 'job_title', 'bio', 'profile_picture']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'role': forms.Select(attrs={
                'class': 'form-select',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-input',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
        }


class PasswordChangeForm(SetPasswordForm):
    """
    Form for users to change their password.
    """
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter current password',
        })
    )
    
    field_order = ['old_password', 'new_password1', 'new_password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter new password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm new password',
        })
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Your current password is incorrect.')
        return old_password
