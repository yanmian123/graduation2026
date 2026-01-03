from django.contrib import admin
from .models import Article, Attachment, Comment, Like, Collection, Follow

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """文章管理界面"""
    list_display = ('title', 'user', 'category', 'view_count', 'like_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'user__username', 'content')
    readonly_fields = ('view_count', 'like_count', 'star_count', 'comment_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'title', 'category', 'tags')}),
        ('内容信息', {'fields': ('content',)}),
        ('统计信息', {'fields': ('view_count', 'like_count', 'star_count', 'comment_count')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """附件管理界面"""
    list_display = ('article', 'file', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('article__title',)
    readonly_fields = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理界面"""
    list_display = ('article', 'user', 'created_at', 'like_count')
    list_filter = ('created_at',)
    search_fields = ('article__title', 'user__username', 'content')
    readonly_fields = ('created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """点赞管理界面"""
    list_display = ('user', 'article', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """收藏管理界面"""
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """关注管理界面"""
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'followed__username')