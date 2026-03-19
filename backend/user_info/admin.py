from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from .models import VerificationApplication, SensitiveWord

@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    """敏感词管理"""
    list_display = ('word', 'created_at')
    search_fields = ('word',)
    list_filter = ('created_at',)

@admin.register(VerificationApplication)
class VerificationApplicationAdmin(admin.ModelAdmin):
    """实名认证申请管理"""
    list_display = ['id', 'user', 'verification_type', 'status', 'name', 'phone', 'created_at']
    list_filter = ['status', 'verification_type', 'created_at']
    search_fields = ['user__username', 'name', 'id_number', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by', 'business_license_link', 'student_card_link', 'other_files_links']
    change_list_template = 'admin/user_info/verificationapplication/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = VerificationApplication.objects.filter(status='PENDING').count()
        extra_context['pending_count'] = pending_count
        return super().changelist_view(request, extra_context)
    
    def get_fieldsets(self, request, obj=None):
        if obj:
            verification_type = obj.verification_type
            if verification_type == 'ENTERPRISE':
                return (
                    ('基本信息', {
                        'fields': ('user', 'verification_type', 'status')
                    }),
                    ('认证信息', {
                        'fields': ('name', 'id_number', 'phone')
                    }),
                    ('证明文件', {
                        'fields': ('business_license_link', 'other_files_links')
                    }),
                    ('审核信息', {
                        'fields': ('reviewed_by', 'reviewed_at', 'reject_reason')
                    }),
                    ('时间信息', {
                        'fields': ('created_at', 'updated_at')
                    })
                )
            else:
                return (
                    ('基本信息', {
                        'fields': ('user', 'verification_type', 'status')
                    }),
                    ('认证信息', {
                        'fields': ('name', 'id_number', 'phone')
                    }),
                    ('证明文件', {
                        'fields': ('student_card_link', 'other_files_links')
                    }),
                    ('审核信息', {
                        'fields': ('reviewed_by', 'reviewed_at', 'reject_reason')
                    }),
                    ('时间信息', {
                        'fields': ('created_at', 'updated_at')
                    })
                )
        else:
            return (
                ('基本信息', {
                    'fields': ('user', 'verification_type', 'status')
                }),
                ('认证信息', {
                    'fields': ('name', 'id_number', 'phone')
                }),
                ('证明文件', {
                    'fields': ('business_license', 'student_card', 'other_files')
                }),
                ('审核信息', {
                    'fields': ('reviewed_by', 'reviewed_at', 'reject_reason')
                }),
                ('时间信息', {
                    'fields': ('created_at', 'updated_at')
                })
            )
    
    def business_license_link(self, obj):
        if obj.business_license:
            file_path = str(obj.business_license)
            if file_path.startswith('/media/'):
                full_url = file_path
            else:
                full_url = f"{settings.MEDIA_URL}{file_path}"
            return mark_safe(format_html('<a href="{}" target="_blank">查看营业执照</a>', full_url))
        return '-'
    business_license_link.short_description = '营业执照'
    
    def student_card_link(self, obj):
        if obj.student_card:
            file_path = str(obj.student_card)
            if file_path.startswith('/media/'):
                full_url = file_path
            else:
                full_url = f"{settings.MEDIA_URL}{file_path}"
            return mark_safe(format_html('<a href="{}" target="_blank">查看学信网截图</a>', full_url))
        return '-'
    student_card_link.short_description = '学信网截图'
    
    def other_files_links(self, obj):
        if obj.other_files:
            links = []
            for file_url in obj.other_files.split(','):
                if file_url.strip():
                    url = file_url.strip()
                    if url.startswith('/media/'):
                        full_url = url
                    else:
                        full_url = f"{settings.MEDIA_URL}{url}"
                    link_html = '<a href="{}" target="_blank">查看文件</a>'.format(full_url)
                    links.append(mark_safe(link_html))
            return mark_safe('<br>'.join(links))
        return '-'
    other_files_links.short_description = '其他证明文件'
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        """批量通过认证"""
        from notification.utils import create_notification
        
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.status = 'APPROVED'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            create_notification(
                recipient=application.user,
                notification_type='system_general',
                title='认证审核通过',
                message=f'您的{application.get_verification_type_display()}申请已通过审核',
                related_object_id=application.id,
                related_object_type='verification'
            )
            count += 1
        
        self.message_user(request, f'已通过 {count} 个认证申请')
    approve_applications.short_description = '通过选中的认证申请'
    
    def reject_applications(self, request, queryset):
        """批量拒绝认证"""
        from notification.utils import create_notification
        
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.status = 'REJECTED'
            application.reject_reason = '批量拒绝'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            create_notification(
                recipient=application.user,
                notification_type='system_general',
                title='认证审核未通过',
                message=f'您的{application.get_verification_type_display()}申请未通过审核。原因：批量拒绝',
                related_object_id=application.id,
                related_object_type='verification'
            )
            count += 1
        
        self.message_user(request, f'已拒绝 {count} 个认证申请')
    reject_applications.short_description = '拒绝选中的认证申请'
    
    def save_model(self, request, obj, form, change):
        if change and obj.status in ['APPROVED', 'REJECTED'] and not obj.reviewed_by:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            
            from notification.utils import create_notification
            if obj.status == 'APPROVED':
                create_notification(
                    recipient=obj.user,
                    notification_type='system_general',
                    title='认证审核通过',
                    message=f'您的{obj.get_verification_type_display()}申请已通过审核',
                    related_object_id=obj.id,
                    related_object_type='verification'
                )
            elif obj.status == 'REJECTED':
                reject_reason = obj.reject_reason or '未提供原因'
                create_notification(
                    recipient=obj.user,
                    notification_type='system_general',
                    title='认证审核未通过',
                    message=f'您的{obj.get_verification_type_display()}申请未通过审核。原因：{reject_reason}',
                    related_object_id=obj.id,
                    related_object_type='verification'
                )
        super().save_model(request, obj, form, change)
