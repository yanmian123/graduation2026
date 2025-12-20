from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Enterprise, Recruitment, JobApplication
from resume.models import Resume
from .serializers import EnterpriseSerializer, RecruitmentSerializer, JobApplicationSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser # 支持文件上传
from django.db.models import Count, Q
from django.utils import timezone



# 新增：企业联系信息序列化器
class EnterpriseContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ["name", "contact_person", "contact_phone", "contact_email"]
        
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
    parser_classes = [JSONParser,MultiPartParser, FormParser]  # 支持文件上传
    
    def get_queryset(self):
        # 只能查询自己的企业信息
        return Enterprise.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 创建时自动绑定当前登录用户
        serializer.save(user=self.request.user)
        
    # 新增：专门处理logo上传的方法
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_logo(self, request, pk=None):
        enterprise = self.get_object()# 获取当前操作的企业实例（通过 pk 主键）
        if 'logo' in request.FILES:# 检查请求中是否包含 'logo' 文件
            enterprise.logo = request.FILES['logo'] # 保存文件到企业的 logo 字段
            enterprise.save()# 保存企业实例
            return Response({
                'status': 'success',
                'logo_url': enterprise.logo.url # 返回上传后的 logo 访问路径
            })
        return Response(
            {'error': '未提供logo文件'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# 招聘信息视图集
class RecruitmentViewSet(viewsets.ModelViewSet):
    """
    招聘信息管理：
    - 企业用户：CRUD自己的招聘信息
    - 普通用户（求职者）：仅能查看已发布的招聘信息
    """
    serializer_class = RecruitmentSerializer


    def get_permissions(self):
        """动态权限控制"""
        if self.action in ["list", "retrieve", "contact", "apply"]:
            # 这些动作对所有认证用户开放
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "stats":
            # 统计信息需要企业用户
            permission_classes = [permissions.IsAuthenticated]
        else:
            # 其他动作（CRUD）需要企业主权限
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
            return Recruitment.objects.filter(status="PUBLISHED")

    def perform_create(self, serializer):
        """创建招聘信息时，自动关联当前企业"""
        # 确保用户已完善企业信息
        if not hasattr(self.request.user, "enterprise_profile"):
            raise serializers.ValidationError("请先完善企业信息才能发布招聘")
        # 获取前端传递的 is_published 字段
        is_published = self.request.data.get('is_published', True)
        
        serializer.save(
            enterprise=self.request.user.enterprise_profile,
            status="PUBLISHED" if is_published else "DRAFT"
        )

    @action(detail=True, methods=["get"])
    def contact(self, request, pk=None):
        """求职者获取企业联系方式（使用序列化器）"""
        recruitment = self.get_object()
        serializer = EnterpriseContactSerializer(recruitment.enterprise)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取企业招聘统计信息"""
        if not hasattr(request.user, "enterprise_profile"):
            return Response({"error": "请先完善企业信息"}, status=status.HTTP_400_BAD_REQUEST)
        
        enterprise = request.user.enterprise_profile
        recruitments = Recruitment.objects.filter(enterprise=enterprise)
        
        # 统计活跃招聘（已发布且未过期）
        active = recruitments.filter(
            status="PUBLISHED", 
            deadline__gte=timezone.now().date()
        ).count()
        
        # 统计收到的简历（需要根据你的简历模型调整）
        # 这里暂时返回0，你需要根据实际简历模型实现
        resumes = 0
        
        # 统计待面试（需要根据你的面试模型调整）
        # 这里暂时返回0，你需要根据实际面试模型实现
        interviews = 0
        
        data = {
            'active': active,
            'resumes': resumes,
            'interviews': interviews
        }
        
        return Response(data)
    
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """申请职位"""
        recruitment = self.get_object()
        
        # 获取前端传递的简历ID
        resume_id = request.data.get('resume_id')
        if not resume_id:
            return Response(
                {"error": "请选择要投递的简历"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查简历是否存在且属于当前用户
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response(
                {"error": "简历不存在或不属于当前用户"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已经申请过
        if JobApplication.objects.filter(
            recruitment=recruitment, 
            applicant=request.user
        ).exists():
            return Response(
                {"error": "您已经申请过该职位"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建申请记录
        application = JobApplication.objects.create(
            recruitment=recruitment,
            applicant=request.user,
            resume=resume,
            status="PENDING"
        )
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 在文档4的views.py中添加
class JobApplicationViewSet(viewsets.ModelViewSet):
    """职位申请管理"""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 用户只能查看自己的申请记录
        return JobApplication.objects.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        recruitment_id = self.request.data.get('recruitment')
        resume_id = self.request.data.get('resume')
        
        # 检查是否已经申请过
        if JobApplication.objects.filter(
            recruitment_id=recruitment_id, 
            applicant=self.request.user
        ).exists():
            raise serializers.ValidationError("您已经申请过该职位")
        
        # 检查简历是否存在且属于当前用户
        try:
            resume = Resume.objects.get(id=resume_id, user=self.request.user)
        except Resume.DoesNotExist:
            raise serializers.ValidationError("简历不存在或不属于当前用户")
        
        serializer.save(applicant=self.request.user, resume=resume)

