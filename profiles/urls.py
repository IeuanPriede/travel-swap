from django.urls import path
from .views import profile_view, register, edit_profile, custom_logout


urlpatterns = [
    path('register/', register, name='register'),
    path('', profile_view, name='profiles'),
    path('edit/', edit_profile, name='edit_profile'),
    path('logout/', custom_logout, name='logout'),
]