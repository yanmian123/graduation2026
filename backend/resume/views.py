from django.shortcuts import render
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import Resume
from .serializers import ResumeSerializer
import logging
logger = logging.getLogger(__name__) 

#自定义权限：仅允许用户访问和修改自己的简历
class IsResumeOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 验证：当前请求用户 == 简历的 user 字段
        return obj.user == request.user


# 自定义权限：仅允许简历所有者操作（查看/编辑/删除）
class IsResumeOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 验证：当前请求用户 == 简历的 user 字段
        return obj.user == request.user

class ResumeViewSet(viewsets.ModelViewSet):
    """
    简历管理视图集：
    - list: 获取当前用户的所有简历
    - retrieve: 获取单个简历详情
    - create: 创建新简历（自动关联当前用户）
    - update: 全量更新简历（需传所有必填字段）
    - partial_update: 部分更新（如仅修改求职意向）
    - destroy: 删除简历
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsResumeOwner]  # 登录+所有者权限

    # 1. 仅查询当前用户的简历（避免查他人简历）
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    # 2. 传递请求上下文到序列化器（用于 create 方法获取用户）
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})  # 补充请求对象
        return context

    # 3. 自定义创建成功响应（返回更友好的信息）
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
            #  保存简历基本信息（自动关联当前用户）
        resume = self.perform_create(serializer)
        print("请求中的文件：", request.FILES) 
        # 3. 处理上传的PDF文件（如果有）
        pdf_file = request.FILES.get('pdf_file')
        logger.info(f"收到上传文件：{pdf_file.name if pdf_file else '无'}") 
        print(f"收到上传文件：{pdf_file.name if pdf_file else '无'}")
        if pdf_file:
            resume.pdf_url = pdf_file  # 保存文件到模型的FileField
            resume.save()  # 再次保存更新文件路径
            logger.info(f"文件保存成功：{pdf_file.name}")
        # self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "code": 200,
                "message": "简历创建成功",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    # 确保perform_create返回创建的实例
    def perform_create(self, serializer):
        return serializer.save() 

    # 4. 自定义更新成功响应
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # 处理文件上传
        pdf_file = request.FILES.get('pdf_file')
        # 处理文件上传
        if pdf_file:
            # 删除旧文件
            if instance.pdf_url:
                instance.pdf_url.delete(save=False)
            # 保存新文件到实例
            instance.pdf_url = pdf_file
            instance.save()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "code": 200,
                "message": "简历更新成功",
                "data": serializer.data
            }
        )
    
    @action(detail=True, methods=['post'], url_path='delete-pdf')
    def delete_pdf(self, request, pk=None):
        """删除简历的PDF文件"""
        resume = self.get_object()
        
        if not resume.pdf_url:
            return Response(
                {"code": 400, "message": "该简历没有PDF文件"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 删除PDF文件
        resume.pdf_url.delete(save=False)  # 删除文件
        resume.pdf_url = None  # 清空字段
        resume.save()
        
        return Response({
            "code": 200,
            "message": "PDF文件删除成功",
            "data": ResumeSerializer(resume).data
        })
    
class PdfUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsResumeOwner]  # 仅登录用户可上传

    def post(self, request):
        # 获取上传的文件
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({'error': '请选择文件'}, status=400)

        # 关联到简历（如果有resume_id参数）
        resume_id = request.data.get('resume_id')
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                resume.pdf_url = pdf_file  # 保存文件到模型
                resume.save()
                return Response({
                    'success': True,
                    'pdf_url': resume.pdf_url.url  # 返回文件访问URL
                })
            except Resume.DoesNotExist:
                return Response({'error': '简历不存在'}, status=404)
        else:
            # 如果不需要关联简历，直接保存文件（可选）
            # 这里可根据需求处理，例如返回文件URL
            return Response({'error': '请指定简历ID'}, status=400)

