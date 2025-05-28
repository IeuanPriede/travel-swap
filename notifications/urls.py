from django.urls import path
from . import views

urlpatterns = [
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('dismiss/<int:notification_id>/',
         views.dismiss_notification, name='dismiss_notification'),
    path('read/<int:notification_id>/',
         views.mark_notification_read, name='mark_notification_read'),
]
