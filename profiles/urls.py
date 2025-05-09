from django.urls import path
from .views import profile_view, register


urlpatterns = [
    path('register/', register, name='register'),
    path('', profile_view, name='profiles'),
]