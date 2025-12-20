from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.conf import settings
# Create your models here.
class Resume(models.Model):
    STATUS_CHOICES1 = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    STATUS_CHOICES2 = [
        ('M', '男'),
        ('F', '女'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE,related_name="resumes")  # 关联用户
    name = models.CharField(max_length=50,blank=True,verbose_name="姓名")  # 姓名
    sex = models.CharField(max_length=10,blank=True,choices=STATUS_CHOICES2,verbose_name="性别")  # 性别
    email = models.EmailField(blank=True,verbose_name="邮箱")  # 邮箱
    phone = models.CharField(max_length=20,blank=True)  # 电话
    education = models.CharField(max_length=50, blank=True,verbose_name='学历')
    internship_experience= models.TextField(blank=True, verbose_name='实习经历')
    work_experience = models.TextField(blank=True, verbose_name='工作经历') 
    project_experience = models.TextField(blank=True, verbose_name='项目经历')
    school_experience = models.TextField(blank=True, verbose_name='校园经历')
    self_evaluation = models.TextField(blank=True, verbose_name='自我评价')
    scholarships = models.TextField(blank=True, verbose_name='奖学金')
    skills = models.CharField(max_length=500, blank=True, verbose_name='技能标签')
    job_objective= models.CharField(max_length=100, blank=True, verbose_name='求职意向')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES1, default='draft', verbose_name='状态')
    pdf_url = models.URLField(blank=True, null=True, verbose_name='PDF地址')  # 预留
    version = models.IntegerField(default=1, verbose_name='版本号') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_url = models.FileField(upload_to='resumes/pdf/', null=True, blank=True)  # 保存PDF路径
    
    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'
        ordering = ['-updated_at']  # 按更新时间倒序
        
