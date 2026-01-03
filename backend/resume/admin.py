from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    """简历管理界面"""
    list_display = ('name', 'user', 'job_objective', 'status', 'version', 'created_at')
    list_filter = ('status', 'sex', 'education', 'created_at')
    search_fields = ('name', 'user__username', 'job_objective', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {'fields': ('user', 'name', 'sex', 'email', 'phone')}),
        ('教育背景', {'fields': ('education',)}),
        ('经历信息', {'fields': ('internship_experience', 'work_experience', 'project_experience', 'school_experience')}),
        ('其他信息', {'fields': ('self_evaluation', 'scholarships', 'skills')}),
        ('求职意向', {'fields': ('job_objective',)}),
        ('状态信息', {'fields': ('status', 'pdf_url', 'version')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )