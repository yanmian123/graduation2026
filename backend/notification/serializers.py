from rest_framework import serializers
from .models import Notification, Announcement

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'related_object_id', 'related_object_type', 'comment_id', 'created_at', 'recipient_id']
        read_only_fields = ['created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'announcement_type', 'is_active', 'priority', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
