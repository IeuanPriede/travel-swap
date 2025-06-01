from notifications.models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {'unread_notifications': unread}
    return {'unread_notifications': []}
