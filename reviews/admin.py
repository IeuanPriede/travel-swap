from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewee__username')
    list_filter = ('rating', 'created_at')

    def short_comment(self, obj):
        return obj.comment[:50] + "..." if len(
            obj.comment) > 50 else obj.comment
    short_comment.short_description = "Comment"
