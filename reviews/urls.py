from django.urls import path
from . import views

urlpatterns = [
    path('review/<int:user_id>/', views.leave_review, name='leave_review'),
    path('delete/<int:user_id>/', views.delete_review, name='delete_review'),
]
