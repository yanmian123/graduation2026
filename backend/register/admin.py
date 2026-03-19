from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.html import format_html, mark_safe
from django.utils import timezone

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'nickname', 'is_enterprise', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_enterprise', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'nickname')
    ordering = ('-date_joined',)
    actions = ['freeze_users', 'unfreeze_users']
    change_list_template = 'admin/register/user/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # 统计信息
        from enterprise.models import Enterprise, Recruitment
        from article_publish.models import Article
        from enterprise.models import JobApplication
        
        # 统计用户数据
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(days=7)).count()
        enterprise_users = User.objects.filter(is_enterprise=True).count()
        regular_users = User.objects.filter(is_enterprise=False).count()
        total_recruitments = Recruitment.objects.count()
        published_recruitments = Recruitment.objects.filter(status='PUBLISHED').count()
        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(is_draft=False).count()
        total_applications = JobApplication.objects.count()
        
        extra_context['stats'] = {
            'total_users': total_users,
            'active_users': active_users,
            'enterprise_users': enterprise_users,
            'regular_users': regular_users,
            'total_recruitments': total_recruitments,
            'published_recruitments': published_recruitments,
            'total_articles': total_articles,
            'published_articles': published_articles,
            'total_applications': total_applications,
        }
        
        return super().changelist_view(request, extra_context)
    
    # 在用户编辑页面显示自定义字段
    fieldsets = UserAdmin.fieldsets + (
        ('个人信息', {'fields': ('nickname', 'sex', 'age')}),
        ('教育背景', {'fields': ('graduation_school', 'education_level', 'major', 'graduation_year')}),
        ('求职信息', {'fields': ('current_status', 'intended_position', 'intended_salary', 'intended_city')}),
        ('联系方式', {'fields': ('phone_number', 'address')}),
        ('个人简介', {'fields': ('personal_profile',)}),
        ('用户类型', {'fields': ('is_enterprise',)}),
    )
    
    def freeze_users(self, request, queryset):
        """批量冻结用户"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功冻结 {updated} 个用户。')
    freeze_users.short_description = '冻结选中的用户'
    
    def unfreeze_users(self, request, queryset):
        """批量解冻用户"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功解冻 {updated} 个用户。')
    unfreeze_users.short_description = '解冻选中的用户'