"""
URL configuration for staffly project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    """Redirect home to dashboard or login."""
    if request.user.is_authenticated:
        return redirect('dashboard:router')
    return redirect('accounts:login')


urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Customize admin site
admin.site.site_header = 'Staffly Administration'
admin.site.site_title = 'Staffly Admin'
admin.site.index_title = 'Welcome to Staffly Administration'
