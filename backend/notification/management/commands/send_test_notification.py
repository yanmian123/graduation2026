#!/usr/bin/env python
"""
测试通知功能的命令
用于发送测试通知给指定用户
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notification.utils import create_notification

User = get_user_model()

class Command(BaseCommand):
    help = '发送测试通知给指定用户'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='用户ID')
        parser.add_argument('--type', type=str, default='system_general', help='通知类型')
        parser.add_argument('--title', type=str, default='测试通知', help='通知标题')
        parser.add_argument('--message', type=str, default='这是一条测试通知', help='通知内容')

    def handle(self, *args, **options):
        user_id = options['user_id']
        notification_type = options['type']
        title = options['title']
        message = options['message']

        try:
            user = User.objects.get(id=user_id)
            
            # 创建并发送测试通知
            notification = create_notification(
                recipient=user,
                notification_type=notification_type,
                title=title,
                message=message
            )

            self.stdout.write(self.style.SUCCESS(f'✅ 成功发送测试通知给用户 {user.id} - {user.username}'))
            self.stdout.write(f'📋 通知详情:')
            self.stdout.write(f'   ID: {notification.id}')
            self.stdout.write(f'   类型: {notification.get_notification_type_display()}')
            self.stdout.write(f'   标题: {notification.title}')
            self.stdout.write(f'   内容: {notification.message}')
            self.stdout.write(f'   时间: {notification.created_at}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ 用户ID {user_id} 不存在'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 发送通知失败: {str(e)}'))