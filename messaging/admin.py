from django.contrib import admin
from .models import Message, BookingRequest


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'content')
    list_filter = ('timestamp',)

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'sender', 'recipient', 'requested_dates',
        'status', 'created_at', 'responded_at')
    list_filter = ('status', 'created_at', 'responded_at')
    search_fields = (
        'sender__username', 'recipient__username', 'requested_dates')
