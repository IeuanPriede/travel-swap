from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def dismiss_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user)
    if request.method == "POST":
        notification.is_read = True
        notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))
