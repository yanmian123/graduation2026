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
        elif isinstance(obj, JobApplication):
                        # 企业用户只能操作自己企业的申请
            return obj.recruitment.enterprise.user == request.user
        return False
    
# 新增：混合权限类
class IsEnterpriseUser(permissions.BasePermission):
    """验证用户是否为企业用户"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'enterprise_profile')

class IsJobSeeker(permissions.BasePermission):
    """验证用户是否为求职者"""
    def has_permission(self, request, view):
        return not hasattr(request.user, 'enterprise_profile')
    
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
        if self.action in ["list", "retrieve", "contact"]:
            # 这些动作对所有认证用户开放
            permission_classes = [permissions.IsAuthenticated, IsJobSeeker]
        elif self.action == "stats":
            # 统计信息需要企业用户
            permission_classes = [permissions.IsAuthenticated,IsEnterpriseUser]
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
        
        # 统计活跃招聘
        active = recruitments.filter(
            status="PUBLISHED", 
            deadline__gte=timezone.now().date()
        ).count()
        
        # 统计收到的申请
        applications_count = JobApplication.objects.filter(
            recruitment__enterprise=enterprise
        ).count()
        
        # 统计待面试
        pending_interviews = JobApplication.objects.filter(
            recruitment__enterprise=enterprise,
            status="INTERVIEW"
        ).count()
        
        data = {
            'active_recruitments': active,
            'total_applications': applications_count,
            'pending_interviews': pending_interviews
        }
        
        return Response(data)
    
    
    # @action(detail=True, methods=['post'])
    # def apply(self, request, pk=None):
    #     """申请职位"""
    #     recruitment = self.get_object()
        
    #     # 获取前端传递的简历ID
    #     resume_id = request.data.get('resume_id')
    #     if not resume_id:
    #         return Response(
    #             {"error": "请选择要投递的简历"}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     # 检查简历是否存在且属于当前用户
    #     try:
    #         resume = Resume.objects.get(id=resume_id, user=request.user)
    #     except Resume.DoesNotExist:
    #         return Response(
    #             {"error": "简历不存在或不属于当前用户"}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     # 检查是否已经申请过
    #     if JobApplication.objects.filter(
    #         recruitment=recruitment, 
    #         applicant=request.user
    #     ).exists():
    #         return Response(
    #             {"error": "您已经申请过该职位"}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     # 创建申请记录
    #     application = JobApplication.objects.create(
    #         recruitment=recruitment,
    #         applicant=request.user,
    #         resume=resume,
    #         status="PENDING"
    #     )
        
    #     serializer = JobApplicationSerializer(application)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# 在文档4的views.py中添加
class JobApplicationViewSet(viewsets.ModelViewSet):
    """职位申请管理"""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """根据动作动态设置权限"""
        if self.action in ["create", "my_applications"]:
            # 创建申请和查看自己的申请需要求职者权限
            permission_classes = [permissions.IsAuthenticated, IsJobSeeker]
        elif self.action in ["list", "retrieve", "update", "partial_update"]:
            # 这些动作需要根据对象权限判断
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'enterprise_profile'):
            enterprise = user.enterprise_profile
            return JobApplication.objects.filter(
                recruitment__enterprise=enterprise
            ).select_related('applicant', 'recruitment','recruitment__enterprise')
        else:
            return JobApplication.objects.filter(applicant=user)

    def get_serializer_context(self):
        """为序列化器提供额外的上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # 在 views.py 中修改 JobApplicationViewSet 的 perform_create
    def perform_create(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        
        # 从验证后的数据获取对象
        recruitment = serializer.validated_data.get('recruitment')
        resume = serializer.validated_data.get('resume')
        
        logger.info(f"开始创建申请记录，recruitment: {recruitment.id}, resume: {resume.id if resume else 'None'}")
        
        # 检查是否已经申请过（双重验证）
        if JobApplication.objects.filter(
            recruitment=recruitment, 
            applicant=self.request.user
        ).exists():
            logger.warning("用户已申请过该职位")
            raise serializers.ValidationError("您已经申请过该职位")
        
        # 获取原简历（用于创建快照）
        original_resume = resume
        if not original_resume:
            logger.error("未提供简历")
            raise serializers.ValidationError("必须提供简历")
        
        # 验证简历属于当前用户
        if original_resume.user != self.request.user:
            logger.error("简历不属于当前用户")
            raise serializers.ValidationError("简历不属于当前用户")
        
        # 创建简历快照
        resume_snapshot = self._create_resume_snapshot(original_resume)
        logger.info(f"创建的快照数据: {resume_snapshot}")
        
        # 复制PDF文件
        pdf_file = self._copy_pdf_file(original_resume)
        
        try:
            # 保存申请记录（resume设为None，使用快照）
            application = serializer.save(
                applicant=self.request.user, 
                resume=None,  # 关键：不关联原始简历
                resume_snapshot=resume_snapshot,
                pdf_file=pdf_file
            )
            
            logger.info(f"成功创建申请记录，ID: {application.id}")
            return application
            
        except Exception as e:
            logger.error(f"创建申请记录失败: {str(e)}")
            raise

    def _copy_pdf_file(self, resume):
        """简化PDF处理 - 直接返回None，不复制文件"""
        return None

    def _create_resume_snapshot(self, resume):
        """创建简历快照"""
        snapshot = {
            'name': resume.name,
            'sex': resume.sex,
            'email': resume.email,
            'phone': resume.phone,
            'education': resume.education,
            'job_objective': resume.job_objective,
            'internship_experience': resume.internship_experience,
            'work_experience': resume.work_experience,
            'project_experience': resume.project_experience,
            'school_experience': resume.school_experience,
            'self_evaluation': resume.self_evaluation,
            'skills': resume.skills,
            'snapshot_created_at': timezone.now().isoformat(),
            'original_resume_id': resume.id,
            'has_pdf': bool(resume.pdf_url)  # 标记是否有PDF文件
        }
        return snapshot

    def perform_create(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        
        recruitment = serializer.validated_data.get('recruitment')
        resume = serializer.validated_data.get('resume')
        
        logger.info(f"开始创建申请记录，recruitment: {recruitment.id}, resume: {resume.id if resume else 'None'}")
        
        # 检查是否已经申请过（双重验证）
        if JobApplication.objects.filter(
            recruitment=recruitment, 
            applicant=self.request.user
        ).exists():
            logger.warning("用户已申请过该职位")
            raise serializers.ValidationError("您已经申请过该职位")
        
        # 获取原简历（用于创建快照）
        original_resume = resume
        if not original_resume:
            logger.error("未提供简历")
            raise serializers.ValidationError("必须提供简历")
        
        # 验证简历属于当前用户
        if original_resume.user != self.request.user:
            logger.error("简历不属于当前用户")
            raise serializers.ValidationError("简历不属于当前用户")
        
        # 创建简历快照
        resume_snapshot = self._create_resume_snapshot(original_resume)
        logger.info(f"创建的快照数据: {resume_snapshot}")
        
        try:
            # 保存申请记录（不关联原始简历，使用快照）
            application = serializer.save(
                applicant=self.request.user, 
                resume=None,  # 关键：不关联原始简历
                resume_snapshot=resume_snapshot,
                pdf_file=None  # 不复制PDF文件
            )
            
            logger.info(f"成功创建申请记录，ID: {application.id}")
            return application
            
        except Exception as e:
            logger.error(f"创建申请记录失败: {str(e)}")
            raise

    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """求职者查看自己的申请记录（已通过权限控制）"""
        applications = self.get_queryset()
        page = self.paginate_queryset(applications)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """企业更新申请状态"""
        application = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {"error": "必须提供状态参数"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证状态值
        valid_statuses = [choice[0] for choice in JobApplication._meta.get_field('status').choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": "无效的状态值"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def enterprise_stats(self, request):
        """企业查看申请统计"""
        if not hasattr(request.user, 'enterprise_profile'):
            return Response(
                {"error": "只有企业用户才能查看统计"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        enterprise = request.user.enterprise_profile
        
        # 按状态统计
        status_stats = JobApplication.objects.filter(
            recruitment__enterprise=enterprise
        ).values('status').annotate(count=Count('id'))
        
        # 最近30天申请趋势
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_trend = JobApplication.objects.filter(
            recruitment__enterprise=enterprise,
            applied_at__gte=thirty_days_ago
        ).extra({'date': "date(applied_at)"}).values('date').annotate(count=Count('id'))
        
        data = {
            'status_stats': list(status_stats),
            'recent_trend': list(recent_trend)
        }
        
        return Response(data)
