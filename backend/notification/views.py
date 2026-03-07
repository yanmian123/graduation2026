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
