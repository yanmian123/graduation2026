from django.db import models
from register.models import User

class VerificationStatus(models.TextChoices):
    """认证状态"""
    PENDING = 'PENDING', '待审核'
    APPROVED = 'APPROVED', '已通过'
    REJECTED = 'REJECTED', '已拒绝'

class SensitiveWord(models.Model):
    """敏感词模型"""
    word = models.CharField(max_length=100, unique=True, verbose_name='敏感词')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '敏感词'
        verbose_name_plural = '敏感词'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.word

class VerificationApplication(models.Model):
    """实名认证申请"""
    VERIFICATION_TYPES = [
        ('ENTERPRISE', '企业认证'),
        ('INDIVIDUAL', '个人认证')
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_applications',
        verbose_name='申请人'
    )
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPES,
        verbose_name='认证类型'
    )
    
    status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        verbose_name='审核状态'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='真实姓名'
    )
    
    id_number = models.CharField(
        max_length=18,
        verbose_name='身份证号'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='联系电话'
    )
    
    business_license = models.FileField(
        upload_to='verifications/business_licenses/',
        null=True,
        blank=True,
        verbose_name='营业执照'
    )
    
    student_card = models.FileField(
        upload_to='verifications/student_cards/',
        null=True,
        blank=True,
        verbose_name='学信网截图'
    )
    
    other_files = models.JSONField(
        default=list,
        verbose_name='其他证明文件',
        help_text='存储其他证明文件的URL列表'
    )
    
    reject_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='拒绝原因'
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_verifications',
        verbose_name='审核人'
    )
    
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='审核时间'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '认证申请'
        verbose_name_plural = '认证申请'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['verification_type', 'status'])
        ]
    
    def __str__(self):
        return f'{self.get_verification_type_display()} - {self.user.username} ({self.get_status_display()})'
