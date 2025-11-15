from django.db import models
from register.models import User
# Create your models here.
class Enterprise(models.Model):
    """企业信息表（关联系统用户）"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="enterprise_profile",  # 反向关联：user.enterprise_profile
        verbose_name="关联用户"
    )
    name = models.CharField(max_length=200, verbose_name="企业名称")
    logo = models.ImageField(
        upload_to="enterprise/logos/", 
        null=True, 
        blank=True, 
        verbose_name="企业Logo"
    )
    description = models.TextField(verbose_name="企业简介")
    contact_person = models.CharField(max_length=50, verbose_name="联系人")
    contact_phone = models.CharField(max_length=20, verbose_name="联系电话")
    contact_email = models.EmailField(verbose_name="联系邮箱")
    address = models.CharField(max_length=500, verbose_name="企业地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "企业信息"
        verbose_name_plural = "企业信息"

class Recruitment(models.Model):
    """招聘信息表（关联企业）"""
    enterprise = models.ForeignKey(
        Enterprise, 
        on_delete=models.CASCADE, 
        related_name="recruitments", 
        verbose_name="所属企业"
    )
    title = models.CharField(max_length=200, verbose_name="招聘标题")
    job = models.CharField(max_length=100, verbose_name="职位名称")
    work_location = models.CharField(max_length=200, verbose_name="工作地点")
    salary = models.CharField(max_length=100, verbose_name="薪资范围")  # 如"10k-20k/月"
    experience = models.CharField(max_length=100, verbose_name="工作经验要求")  # 如"3-5年"
    education = models.CharField(max_length=50, verbose_name="学历要求")  # 如"本科及以上"
    job_desc = models.TextField(verbose_name="职位描述")  # 岗位职责
    job_require = models.TextField(verbose_name="任职要求")
    is_published = models.BooleanField(default=True, verbose_name="是否发布")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]  # 按发布时间倒序
        verbose_name = "招聘信息"
        verbose_name_plural = "招聘信息"

    def __str__(self):
        return f"{self.enterprise.name} - {self.job}"