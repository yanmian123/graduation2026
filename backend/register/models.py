from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """自定义用户模型，继承自AbstractUser，可以根据需要添加额外的字段"""
    nickname = models.CharField(max_length=30, blank=True, null=True,verbose_name="用户昵称")  # 昵称
    sex = models.CharField(max_length=10, blank=True, null=True,verbose_name="性别")  # 性别 
    age = models.IntegerField(blank=True, null=True,verbose_name="年龄")  # 年龄
    graduation_school = models.CharField(max_length=100, blank=True, null=True,verbose_name="毕业学校")  # 毕业学校
    education_level = models.CharField(max_length=50, blank=True, null=True,verbose_name="学历")  # 学历
    major = models.CharField(max_length=100, blank=True, null=True,verbose_name="专业")  # 专业
    graduation_year = models.IntegerField(blank=True, null=True,verbose_name="毕业年份")  # 毕业年份
    phone_number = models.CharField(max_length=15, blank=True, null=True,verbose_name="电话号码")  # 电话号码
    current_status = models.CharField(max_length=100, blank=True, null=True,verbose_name="当前状态")  # 当前状态（如在职、待业等）
    intended_position = models.CharField(max_length=100, blank=True, null=True,verbose_name="意向职位")  # 意向职位
    intended_salary = models.CharField(max_length=50, blank=True, null=True,verbose_name="意向薪资")  # 意向薪资
    address = models.CharField(max_length=255, blank=True, null=True,verbose_name="地址")  # 地址
    intended_city = models.CharField(max_length=100, blank=True, null=True,verbose_name="意向城市")  # 意向城市
    personal_profile = models.TextField(max_length=600,blank=True, null=True,verbose_name="个人简介")  # 个人简介
    is_enterprise = models.BooleanField(default=False, verbose_name="是否企业用户")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="用户头像")
# Create your models here.
    class Meta:
        verbose_name = "用户"  # 单数显示名称（在admin后台等地方显示）
        verbose_name_plural = "用户"  # 复数显示名称（避免自动加s）
        ordering = ['-date_joined']  # 按注册时间倒序排序（最新注册的在前）