from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Enterprise, Recruitment
from .serializers import EnterpriseSerializer, RecruitmentSerializer

# 自定义权限：仅企业主能操作自己的信息
class IsEnterpriseOwner(permissions.BasePermission):
    """验证对象是否属于当前企业用户"""
    def has_object_permission(self, request, view, obj):
        # 对于Enterprise模型：obj.user == 当前用户
        # 对于Recruitment模型：obj.enterprise.user == 当前用户
        if isinstance(obj, Enterprise):
            return obj.user == request.user
        elif isinstance(obj, Recruitment):
            return obj.enterprise.user == request.user
        return False

# 企业信息视图集
class EnterpriseViewSet(viewsets.ModelViewSet):
    """
    企业用户管理自己的信息：
    - 列表/详情：仅能查看自己的企业信息
    - 创建：自动关联当前登录用户
    - 更新/删除：仅能操作自己的信息
    """
    serializer_class = EnterpriseSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnterpriseOwner]

    def get_queryset(self):
        # 只能查询自己的企业信息
        return Enterprise.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 创建时自动绑定当前登录用户
        serializer.save(user=self.request.user)

# 招聘信息视图集
class RecruitmentViewSet(viewsets.ModelViewSet):
    """
    招聘信息管理：
    - 企业用户：CRUD自己的招聘信息
    - 普通用户（求职者）：仅能查看已发布的招聘信息
    """
    serializer_class = RecruitmentSerializer

    def get_permissions(self):
        """动态权限：列表/详情允许所有登录用户；创建/修改仅企业主"""
        if self.action in ["list", "retrieve", "contact"]:
            # 求职者可查看
            permission_classes = [permissions.IsAuthenticated]
        else:
            # 企业主才能创建/修改
            permission_classes = [permissions.IsAuthenticated, IsEnterpriseOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """动态查询集：企业查自己的，求职者查已发布的"""
        user = self.request.user
        # 检查用户是否有企业信息（即是否为企业用户）
        if hasattr(user, "enterprise_profile"):
            # 企业用户：查看自己的所有招聘信息
            return Recruitment.objects.filter(enterprise=user.enterprise_profile)
        else:
            # 普通用户（求职者）：仅查看已发布的
            return Recruitment.objects.filter(is_published=True)

    def perform_create(self, serializer):
        """创建招聘信息时，自动关联当前企业"""
        # 确保用户已完善企业信息
        if not hasattr(self.request.user, "enterprise_profile"):
            raise serializers.ValidationError("请先完善企业信息才能发布招聘")
        serializer.save(enterprise=self.request.user.enterprise_profile)

    @action(detail=True, methods=["get"])
    def contact(self, request, pk=None):
        """求职者获取企业联系方式（仅返回联系信息，隐藏敏感字段）"""
        recruitment = self.get_object()
        contact_data = {
            "enterprise_name": recruitment.enterprise.name,
            "contact_person": recruitment.enterprise.contact_person,
            "contact_phone": recruitment.enterprise.contact_phone,
            "contact_email": recruitment.enterprise.contact_email
        }
        return Response(contact_data)