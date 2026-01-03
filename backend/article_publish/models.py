from django.db import models
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
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following',verbose_name="关注用户")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers',verbose_name="被关注用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        unique_together = ['follower', 'followed']  # 防止重复关注
        verbose_name="关注记录"
        ordering=['-created_at'] 