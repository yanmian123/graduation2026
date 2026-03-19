from django.contrib import admin
from .models import Article, Report

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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """举报管理界面"""
    list_display = ('id', 'reporter', 'reported_user', 'report_type', 'reason', 'status', 'created_at')
    list_filter = ('status', 'report_type', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'reason', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    actions = ['approve_reports', 'reject_reports']
    
    def save_model(self, request, obj, form, change):
        """保存举报记录时检查状态变化并发送通知"""
        super().save_model(request, obj, form, change)
    
    def send_approval_notification(self, report):
        """发送举报通过通知"""
        from notification.utils import create_notification
        
        feedback = report.admin_feedback if report.admin_feedback else ''
        feedback_text = f'。{feedback}' if feedback else ''
        
        create_notification(
            recipient=report.reporter,
            notification_type='report_approved',
            title='举报处理结果',
            message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已通过处理{feedback_text}',
            related_object_id=report.id,
            related_object_type='report'
        )
        
        create_notification(
            recipient=report.reported_user,
            notification_type='user_reported',
            title='账号被举报',
            message=f'您的账号因"{report.reason}"被举报，已通过处理{feedback_text}',
            related_object_id=report.id,
            related_object_type='report'
        )
    
    def send_rejection_notification(self, report):
        """发送举报拒绝通知"""
        from notification.utils import create_notification
        
        feedback = report.admin_feedback if report.admin_feedback else ''
        feedback_text = f'。{feedback}' if feedback else ''
        
        create_notification(
            recipient=report.reporter,
            notification_type='report_rejected',
            title='举报处理结果',
            message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已被拒绝{feedback_text}',
            related_object_id=report.id,
            related_object_type='report'
        )
    
    def approve_reports(self, request, queryset):
        """批量通过举报"""
        count = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'成功通过 {count} 条举报。')
        
        # 发送通知给举报人和被举报人
        from notification.utils import create_notification
        for report in queryset.filter(status='approved'):
            # 通知举报人
            create_notification(
                recipient=report.reporter,
                notification_type='report_approved',
                title='举报处理结果',
                message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已通过处理。',
                related_object_id=report.id,
                related_object_type='report'
            )
            # 通知被举报人
            create_notification(
                recipient=report.reported_user,
                notification_type='user_reported',
                title='账号被举报',
                message=f'您的账号因"{report.reason}"被举报，已通过处理。',
                related_object_id=report.id,
                related_object_type='report'
            )
    
    approve_reports.short_description = '批量通过举报'
    
    def reject_reports(self, request, queryset):
        """批量拒绝举报"""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'成功拒绝 {count} 条举报。')
        
        # 发送通知给举报人
        from notification.utils import create_notification
        for report in queryset.filter(status='rejected'):
            create_notification(
                recipient=report.reporter,
                notification_type='report_rejected',
                title='举报处理结果',
                message=f'您对{report.reported_user.nickname or report.reported_user.username}的举报已被拒绝。',
                related_object_id=report.id,
                related_object_type='report'
            )
    
    reject_reports.short_description = '批量拒绝举报'
