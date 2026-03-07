from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """文章管理界面"""
    list_display = ('title', 'user', 'category', 'view_count', 'like_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'user__username', 'content')
    readonly_fields = ('view_count', 'like_count', 'star_count', 'comment_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['delete_articles']
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'title', 'category', 'tags')}),
        ('内容信息', {'fields': ('content',)}),
        ('统计信息', {'fields': ('view_count', 'like_count', 'star_count', 'comment_count')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
    
    def delete_articles(self, request, queryset):
        """批量删除文章"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'成功删除 {count} 篇文章。')
    delete_articles.short_description = '批量删除文章'