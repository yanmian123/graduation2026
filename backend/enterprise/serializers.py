from rest_framework import serializers
from .models import Enterprise, Recruitment, JobApplication

class EnterpriseSerializer(serializers.ModelSerializer):
    """企业信息序列化器"""
    username = serializers.CharField(source="user.username", read_only=True)  # 显示关联的用户名

    class Meta:
        model = Enterprise
        fields = [
            "id", "user", "username", "name", "logo", "description",
            "industry", "scale", "contact_person", "contact_phone", 
            "contact_email", "address", "is_verified",
            "created_at", "updated_at"
        ]
        read_only_fields = ["user"] # 用户自动关联，前端无需传递

class RecruitmentSerializer(serializers.ModelSerializer):
    """招聘信息序列化器"""
    enterprise_name = serializers.CharField(source="enterprise.name", read_only=True)  # 冗余显示企业名称
    enterprise_id = serializers.IntegerField(source="enterprise.id", read_only=True)
    is_published = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruitment
        fields = [
            "id", "enterprise", "enterprise_name", "enterprise_id",
            "title","job", "job_type", "work_location", "salary",
            "number_of_recruits", "experience", "education",
            "job_desc", "job_require", "status","is_published", "is_urgent",
            "deadline", "created_at", "updated_at"
        ]
        read_only_fields = ["enterprise"]  # 自动关联当前企业，前端无需传递
        
    def get_is_published(self, obj):
        """将 status 字段映射为 is_published 布尔值"""
        return obj.status == "PUBLISHED"

    def create(self, validated_data):
        # 处理前端传递的 is_published 字段
        is_published = self.context['request'].data.get('is_published', True)
        if is_published:
            validated_data['status'] = "PUBLISHED"
        else:
            validated_data['status'] = "DRAFT"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_published = self.context['request'].data.get('is_published')
        if is_published is not None:
            if is_published:
                validated_data['status'] = "PUBLISHED"
            else:
                validated_data['status'] = "DRAFT"
        return super().update(instance, validated_data)
    
    
# 在文档2中添加
class JobApplicationSerializer(serializers.ModelSerializer):
    recruitment_title = serializers.CharField(source='recruitment.title', read_only=True)
    enterprise_name = serializers.CharField(source='recruitment.enterprise.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    resume_name = serializers.CharField(source='resume.name', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id", "recruitment", "recruitment_title", "applicant", 
            "applicant_name", "resume", "resume_name", "status", 
            "applied_at", "enterprise_name"
        ]
        read_only_fields = ["applicant", "applied_at"]