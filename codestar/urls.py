"""
URL configuration for codestar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from profiles import views as profile_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/', include('profiles.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', profile_views.home, name='home'),
    path('like/', profile_views.like_profile, name='like_profile'),
    path('next/', profile_views.next_profile, name='next_profile'),
    path('about/', profile_views.about, name='about'),
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
    # Password reset URLs
    path(
        'password_reset/', auth_views.PasswordResetView.as_view(),
        name='password_reset'
        ),
    path(
        'password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
         ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
        ),
    path(
        'reset/done/', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
        ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
        )
