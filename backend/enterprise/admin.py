from django.contrib import admin
from .models import Enterprise, Recruitment, JobApplication

@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    """企业管理界面"""
    list_display = ('name', 'user', 'industry', 'scale', 'is_verified', 'created_at')
    list_filter = ('industry', 'scale', 'is_verified', 'created_at')
    search_fields = ('name', 'user__username', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'name', 'logo', 'description')}),
        ('企业详情', {'fields': ('industry', 'scale')}),
        ('联系方式', {'fields': ('contact_person', 'contact_phone', 'contact_email', 'address')}),
        ('认证状态', {'fields': ('is_verified',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    """招聘信息管理界面"""
    list_display = ('title', 'enterprise', 'job_type', 'work_location', 'salary', 'status', 'created_at')
    list_filter = ('job_type', 'status', 'is_urgent', 'education', 'experience', 'created_at')
    search_fields = ('title', 'enterprise__name', 'job')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {'fields': ('enterprise', 'title', 'job_type')}),
        ('工作详情', {'fields': ('work_location', 'salary', 'number_of_recruits')}),
        ('职位要求', {'fields': ('experience', 'education', 'job', 'job_desc', 'job_require')}),
        ('状态信息', {'fields': ('status', 'is_urgent', 'deadline')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """职位申请管理界面"""
    list_display = ('applicant', 'recruitment', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__username', 'recruitment__title')
    readonly_fields = ('applied_at',)
    
    fieldsets = (
        ('申请信息', {'fields': ('recruitment', 'applicant')}),
        ('简历信息', {'fields': ('resume', 'resume_snapshot', 'pdf_file')}),
        ('申请状态', {'fields': ('status',)}),
        ('时间信息', {'fields': ('applied_at',)}),
    )