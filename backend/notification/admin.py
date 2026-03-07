from django.contrib import admin
from .models import Notification, Announcement

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理界面"""
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {'fields': ('recipient', 'notification_type', 'title', 'message')}),
        ('关联信息', {'fields': ('related_object_id', 'related_object_type')}),
        ('状态信息', {'fields': ('is_read',)}),
        ('时间信息', {'fields': ('created_at',)}),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """系统公告管理界面"""
    list_display = ('title', 'announcement_type', 'is_active', 'priority', 'created_by', 'created_at')
    list_filter = ('announcement_type', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'priority')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {'fields': ('title', 'content', 'announcement_type')}),
        ('显示设置', {'fields': ('is_active', 'priority')}),
        ('创建信息', {'fields': ('created_by',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
