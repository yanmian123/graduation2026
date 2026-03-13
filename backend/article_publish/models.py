from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from register.models import User

from django.conf import settings
from django.utils.html import strip_tags

class Article(models.Model):
    '''文章帖子模型'''
    CATEGORY_CHOICES=[
        ('interview','面试经验'),
        ('resume','简历技巧'),
        ('career','行业选择'),
        ('exam','笔试攻略'),
        ('other','其他'),
    ]

    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles",verbose_name="作者")  # 关联用户/作者
    title=models.CharField(max_length=80, verbose_name="标题")
    category=models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="分类")
    tags=models.CharField(max_length=50, blank=True, verbose_name="标签")
    content=models.TextField(verbose_name="内容")
    view_count = models.PositiveIntegerField(default=0,verbose_name="浏览量")
    like_count=models.IntegerField(default=0, verbose_name="点赞数")
    star_count=models.IntegerField(default=0, verbose_name="收藏数")
    comment_count=models.IntegerField(default=0, verbose_name="评论数")
    is_draft=models.BooleanField(default=False, verbose_name="是否为草稿")
    created_at=models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at=models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name='文章帖子'
        verbose_name_plural='文章帖子'
        ordering=['-created_at']  # 按创建时间倒序

    
class Attachment(models.Model):
    '''附件模型，关联文章，可用于存储图片等文件'''
    article=models.ForeignKey(Article, on_delete=models.CASCADE, related_name="attachments", verbose_name="文件所属文章")
    file=models.FileField(upload_to='articles/attachments/', verbose_name="附件文件")
    created_at=models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    
    class Meta:
        verbose_name='文章附件上传'
        verbose_name_plural='文章附件上传'
        ordering=['-created_at']  # 按上传时间倒序
    
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments',verbose_name="评论所属文章")
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="评论者")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    like_count = models.PositiveIntegerField(default=0, verbose_name="评论点赞数")
    class Meta:
        verbose_name='文章评论区'
        ordering=['-created_at'] 

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="点赞用户")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, verbose_name="点赞的文章")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, verbose_name="点赞的评论")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="点赞时间")

    class Meta:
        unique_together = [['user', 'article'], ['user', 'comment']]
        verbose_name="点赞记录" 
        ordering=['-created_at'] 
        
class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="收藏用户")
    article = models.ForeignKey(Article, on_delete=models.CASCADE,verbose_name="收藏的文章")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        unique_together = ['user', 'article']  # 防止重复收藏
        verbose_name="收藏记录"
        ordering=['-created_at'] 
        
class Follow(models.Model):
    FOLLOW_TYPE_CHOICES = [
        ('user', '关注用户'),
        ('enterprise', '关注企业'),
    ]
    
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following',verbose_name="关注用户")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers',verbose_name="被关注用户")
    follow_type = models.CharField(max_length=20, choices=FOLLOW_TYPE_CHOICES, default='user', verbose_name="关注类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        unique_together = ['follower', 'followed', 'follow_type']  # 防止重复关注
        verbose_name="关注记录"
        ordering=['-created_at'] 

class Report(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    REPORT_TYPE_CHOICES = [
        ('user', '举报用户'),
        ('article', '举报文章'),
        ('comment', '举报评论'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made', verbose_name="举报人")
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', verbose_name="被举报用户")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='user', verbose_name="举报类型")
    reason = models.CharField(max_length=200, verbose_name="举报原因")
    description = models.TextField(blank=True, verbose_name="详细描述")
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending', verbose_name="处理状态")
    admin_feedback = models.TextField(blank=True, verbose_name="管理员反馈")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="举报时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name="举报记录"
        ordering=['-created_at']
        
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username}: {self.reason}"


@receiver(post_save, sender=Report)
def send_report_notification(sender, instance, created, **kwargs):
    """举报状态变化时发送通知"""
    if not created:
        try:
            from django.core.cache import cache
            
            # 使用缓存避免重复发送通知
            cache_key = f'report_notification_{instance.id}_{instance.status}'
            if cache.get(cache_key):
                return
            
            if instance.status == 'approved':
                from notification.utils import create_notification
                feedback = instance.admin_feedback if instance.admin_feedback else ''
                feedback_text = f'。{feedback}' if feedback else ''
                
                create_notification(
                    recipient=instance.reporter,
                    notification_type='report_approved',
                    title='举报处理结果',
                    message=f'您对{instance.reported_user.nickname or instance.reported_user.username}的举报已通过处理{feedback_text}',
                    related_object_id=instance.id,
                    related_object_type='report'
                )
                
                create_notification(
                    recipient=instance.reported_user,
                    notification_type='user_reported',
                    title='账号被举报',
                    message=f'您的账号因"{instance.reason}"被举报，已通过处理{feedback_text}',
                    related_object_id=instance.id,
                    related_object_type='report'
                )
                
                cache.set(cache_key, True, 300)
                
            elif instance.status == 'rejected':
                from notification.utils import create_notification
                feedback = instance.admin_feedback if instance.admin_feedback else ''
                feedback_text = f'。{feedback}' if feedback else ''
                
                create_notification(
                    recipient=instance.reporter,
                    notification_type='report_rejected',
                    title='举报处理结果',
                    message=f'您对{instance.reported_user.nickname or instance.reported_user.username}的举报已被拒绝{feedback_text}',
                    related_object_id=instance.id,
                    related_object_type='report'
                )
                
                cache.set(cache_key, True, 300)
        except Exception as e:
            print(f"发送举报通知时出错: {e}")
            import traceback
            traceback.print_exc() 