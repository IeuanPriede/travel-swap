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
from django.contrib import admin
from django.urls import path, include
from profiles.views import profile_view
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/', include('profiles.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='home.html'),
         name='home'
         ),
    path('about/', TemplateView.as_view(template_name='about.html'),
         name='about'
         ),
    path('travel-log/', TemplateView.as_view(template_name='travel_log.html'),
         name='travel_log'
         ),
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
        'reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
        ),
    path(
        'reset/done/', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
        ),
]
