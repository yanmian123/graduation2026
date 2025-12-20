from django.db import models
from register.models import User
from django.core.validators import RegexValidator, MinValueValidator 
from django.utils import timezone
# Create your models here.

# 定义常用选择项常量（便于维护和复用）
INDUSTRY_CHOICES = [
    ("IT", "信息技术"),
    ("FINANCE", "金融"),
    ("EDUCATION", "教育"),
    ("MEDIA", "传媒"),
    ("MANUFACTURING", "制造业"),
    ("SERVICE", "服务业"),
    ("OTHER", "其他")
]

SCALE_CHOICES = [
    ("MICRO", "微型企业（<10人）"),
    ("SMALL", "小型企业（10-99人）"),
    ("MEDIUM", "中型企业（100-999人）"),
    ("LARGE", "大型企业（1000人以上）")
]

JOB_TYPE_CHOICES = [
    ("FULL_TIME", "全职"),
    ("PART_TIME", "兼职"),
    ("INTERNSHIP", "实习")
]

EDUCATION_CHOICES = [
    ("HIGH_SCHOOL", "高中及以下"),
    ("ASSOCIATE", "专科"),
    ("BACHELOR", "本科"),
    ("MASTER", "硕士"),
    ("DOCTOR", "博士及以上")
]

EXPERIENCE_CHOICES = [
    ("FRESH", "应届毕业生"),
    ("LESS_THAN_1", "1年以内"),
    ("1_3", "1-3年"),
    ("3_5", "3-5年"),
    ("5_10", "5-10年"),
    ("MORE_THAN_10", "10年以上")
]

RECRUITMENT_STATUS = [
    ("DRAFT", "草稿"),
    ("PUBLISHED", "已发布"),
    ("EXPIRED", "已过期")
]


class Enterprise(models.Model):
    """企业信息表（关联系统用户）"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="enterprise_profile",  # 反向关联：user.enterprise_profile
        verbose_name="关联用户"
    )
    name = models.CharField(max_length=200, verbose_name="企业名称",help_text="请填写企业全称",db_index=True,unique=True )
    logo = models.ImageField(
        upload_to="enterprise/logos/", 
        null=True, 
        blank=True, 
        #default="enterprise/logos/default.png",  # 设置默认logo
        verbose_name="企业Logo"
    )
    description = models.TextField(verbose_name="企业简介",help_text="请简要介绍企业主营业务、发展历程等")
    industry = models.CharField(
        max_length=20,
        choices=INDUSTRY_CHOICES,
        verbose_name="所属行业",
        help_text="选择企业主要经营领域",
        default="OTHER"
    )
    scale = models.CharField(
        max_length=20,
        choices=SCALE_CHOICES,
        verbose_name="企业规模",
        help_text="选择企业人员规模",
        default="SMALL"
    )
    contact_person = models.CharField(
        max_length=50, 
        verbose_name="联系人",
        help_text="请填写负责招聘的联系人姓名"
        
    )
    contact_phone = models.CharField(
        max_length=20, 
        verbose_name="联系电话",
        validators=[RegexValidator(
            r'^1[3-9]\d{9}$', 
            "请输入有效的手机号码"
        )],
        help_text="请填写有效的手机号码"
    )
    contact_email = models.EmailField(
        verbose_name="联系邮箱",
        help_text="请填写企业官方招聘邮箱"
    )
    address = models.CharField(
        max_length=500, 
        verbose_name="企业地址",
        help_text="请填写详细办公地址"
    )
    is_verified = models.BooleanField(
        default=False, 
        verbose_name="是否认证",
        help_text="标记企业是否通过平台认证"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "企业信息"
        verbose_name_plural = "企业信息"
        ordering = ["-created_at"]

class Recruitment(models.Model):
    """招聘信息表（关联企业）"""
    enterprise = models.ForeignKey(
        Enterprise, 
        on_delete=models.CASCADE, 
        related_name="recruitments", 
        verbose_name="所属企业"
    )
    title = models.CharField(max_length=200, verbose_name="招聘标题",help_text="例如：【急聘】资深Python开发工程师")
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        verbose_name="工作类型",
        help_text="选择全职/兼职/实习",
        default="全职"
    )
    work_location = models.CharField(
        max_length=200, 
        verbose_name="工作地点",
        db_index=True,
        help_text="例如：北京市海淀区中关村",
        default="面议"
    )
    salary = models.CharField(
        max_length=100, 
        verbose_name="薪资范围",
        help_text="例如：10k-20k/月 或 150-300元/天",
        default="面议"
    )
    number_of_recruits = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="招聘人数",
        help_text="填写招聘人数，至少1人",
    )   
    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        verbose_name="工作经验要求",
        default="FRESH"
    )
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        verbose_name="学历要求",
        default="HIGH_SCHOOL"
        
    )
    job = models.TextField(
        verbose_name="职位名称",
        help_text="岗位名称，如“软件工程师”",
        default=""
    )
    job_desc = models.TextField(
        verbose_name="职位描述",
        help_text="详细描述岗位职责、工作内容",
        default=""
    )
    job_require = models.TextField(
        verbose_name="任职要求",
        help_text="详细描述技能要求、资格条件等",
        default=""
    )
    status = models.CharField(
        max_length=20,
        choices=RECRUITMENT_STATUS,
        default="DRAFT",
        verbose_name="招聘状态",
        db_index=True
    )
    is_urgent = models.BooleanField(
        default=False,
        verbose_name="是否急聘",
        help_text="标记为急聘的职位将获得更多曝光",
    )
    deadline = models.DateField(
        verbose_name="截止日期",
        help_text="招聘信息有效期截止日期",
        default=timezone.now().date() + timezone.timedelta(days=30)
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]  # 按发布时间倒序
        verbose_name = "招聘信息"
        verbose_name_plural = "招聘信息"
        indexes = [
            models.Index(fields=["status", "deadline"]),  # 组合索引优化查询
            models.Index(fields=["is_urgent"])
        ]

    def __str__(self):
        return f"{self.enterprise.name} - {self.title}"
    def is_expired(self):
        """判断招聘是否已过期"""
        return self.status == "PUBLISHED" and self.deadline < timezone.now().date()
    

# 在文档1的JobApplication模型后添加新的申请状态和关联简历
class JobApplication(models.Model):
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.ForeignKey('resume.Resume', on_delete=models.CASCADE, null=True, blank=True)  # 关联简历
    status = models.CharField(max_length=20, choices=[
        ("PENDING", "待处理"),
        ("VIEWED", "已查看"), 
        ("INTERVIEW", "待面试"),
        ("REJECTED", "已拒绝"),
        ("HIRED", "已录用")
    ])
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recruitment', 'applicant']  # 防止重复投递
        verbose_name = "职位申请"
        verbose_name_plural = "职位申请"

    def __str__(self):
        return f"{self.applicant.username}申请{self.recruitment.title}"