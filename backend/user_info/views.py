"""
用户信息视图集
"""
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VerificationApplication, SensitiveWord
from .serializers import VerificationApplicationSerializer, VerificationApplicationCreateSerializer
from django.utils import timezone

class IsEnterpriseUser(permissions.BasePermission):
    """验证用户是否为企业用户"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'enterprise_profile')

class SensitiveWordSerializer(serializers.ModelSerializer):
    """敏感词序列化器"""
    class Meta:
        model = SensitiveWord
        fields = '__all__'
        read_only_fields = ['created_at']

class SensitiveWordViewSet(viewsets.ModelViewSet):
    """敏感词管理视图集"""
    queryset = SensitiveWord.objects.all()
    serializer_class = SensitiveWordSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_permissions(self):
        """为不同的 action 设置不同的权限"""
        if self.action == 'check_content':
            # 敏感词检测接口允许所有认证用户访问
            return [permissions.IsAuthenticated()]
        # 其他操作（CRUD）只允许管理员
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def check_content(self, request):
        """检查内容是否包含敏感词"""
        content = request.query_params.get('content', '')
        
        if not content:
            return Response({'has_sensitive': False, 'sensitive_words': []})
        
        # 获取所有敏感词
        sensitive_words = SensitiveWord.objects.values_list('word', flat=True)
        
        # 检查内容中是否包含敏感词
        found_words = []
        for word in sensitive_words:
            if word.lower() in content.lower():
                found_words.append(word)
        
        return Response({
            'has_sensitive': len(found_words) > 0,
            'sensitive_words': found_words
        })

class VerificationViewSet(viewsets.ModelViewSet):
    """认证申请视图集"""
    queryset = VerificationApplication.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VerificationApplicationCreateSerializer
        return VerificationApplicationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 验证用户类型
        verification_type = serializer.validated_data.get('verification_type')
        
        if verification_type == 'ENTERPRISE':
            if not hasattr(self.request.user, 'enterprise_profile'):
                raise permissions.PermissionDenied('只有企业用户才能提交企业认证')
        elif verification_type == 'INDIVIDUAL':
            if hasattr(self.request.user, 'enterprise_profile'):
                raise permissions.PermissionDenied('企业用户不能提交个人认证')
        
        application = serializer.save(user=self.request.user)
        
        from notification.utils import create_notification
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        
        for admin_user in admin_users:
            create_notification(
                recipient=admin_user,
                notification_type='system_general',
                title='新的认证申请',
                message=f'用户 {application.user.username} 提交了{application.get_verification_type_display()}申请，请及时审核',
                related_object_id=application.id,
                related_object_type='verification'
            )
    
    @action(detail=False, methods=['get'])
    def my_application(self, request):
        """获取当前用户的认证申请"""
        try:
            application = VerificationApplication.objects.filter(user=request.user).first()
            if application:
                serializer = self.get_serializer(application)
                return Response(serializer.data)
            return Response({'message': '暂无认证申请'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """管理员：通过认证"""
        try:
            application = self.get_object()
            application.status = 'APPROVED'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            from notification.utils import create_notification
            create_notification(
                recipient=application.user,
                notification_type='system_general',
                title='认证审核通过',
                message=f'您的{application.verification_type_display}申请已通过审核',
                related_object_id=application.id,
                related_object_type='verification'
            )
            
            return Response({'message': '认证已通过'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """管理员：拒绝认证"""
        try:
            application = self.get_object()
            reject_reason = request.data.get('reject_reason', '')
            
            application.status = 'REJECTED'
            application.reject_reason = reject_reason
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            from notification.utils import create_notification
            create_notification(
                recipient=application.user,
                notification_type='system_general',
                title='认证审核未通过',
                message=f'您的{application.verification_type_display}申请未通过审核。原因：{reject_reason}',
                related_object_id=application.id,
                related_object_type='verification'
            )
            
            return Response({'message': '认证已拒绝'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
