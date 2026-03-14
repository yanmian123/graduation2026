from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 只返回当前用户的通知
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        # 普通用户不能直接创建通知，通知由系统或其他操作触发
        return Response({'detail': 'Not allowed to create notifications directly.'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        # 标记单个通知为已读
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})
    
    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        # 标记所有通知为已读
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True)
        return Response({'status': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        # 获取未读通知数量
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['delete'])
    def delete_notification(self, request, pk=None):
        # 删除单个通知
        notification = self.get_object()
        notification.delete()
        return Response({'status': 'Notification deleted'})
    
    @action(detail=False, methods=['delete'])
    def delete_all_read(self, request):
        # 删除所有已读通知
        notifications = self.get_queryset().filter(is_read=True)
        count = notifications.count()
        notifications.delete()
        return Response({'status': f'{count} read notifications deleted'})
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_notification(self, request):
        # 创建通知（用于企业发送通知给求职者）
        from django.contrib.auth import get_user_model
        from .utils import create_notification
        
        recipient_id = request.data.get('recipient_id')
        title = request.data.get('title')
        message = request.data.get('message')
        related_object_id = request.data.get('related_object_id')
        related_object_type = request.data.get('related_object_type')
        
        if not recipient_id or not title or not message:
            return Response(
                {'error': '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        User = get_user_model()
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': '接收者不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 创建通知
        notification = create_notification(
            recipient=recipient,
            notification_type='application_status',
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type
        )
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    
    def get_permissions(self):
        # 查看操作对所有用户开放，其他操作需要管理员权限
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        # 只返回激活的公告，按优先级和创建时间排序
        return Announcement.objects.filter(is_active=True).order_by('-priority', '-created_at')
    
    def perform_create(self, serializer):
        # 创建公告时自动关联当前用户
        serializer.save(created_by=self.request.user)
