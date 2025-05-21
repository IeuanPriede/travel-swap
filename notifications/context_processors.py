from notifications.models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        print("🔔 Context processor - unread for",
              request.user.username, ":", unread.count())
        return {'unread_notifications': unread}
    return {'unread_notifications': []}
