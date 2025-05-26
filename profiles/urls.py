from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('profiles', views.profile_view, name='profiles'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('upload-images/', views.upload_images, name='upload_images'),
    path('delete-profile/', views.delete_profile, name='delete_profile'),
    path(
        'delete-image/<int:image_id>/',
        views.delete_image, name='delete_image'),
    path('', views.home, name='home'),
    path('like/', views.like_profile, name='like_profile'),
    path('next/', views.next_profile, name='next_profile'),
    path('travel-log/', views.travel_log, name='travel_log'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('profile/', views.profile_view, name='profile_view'),
]
