from rest_framework import serializers
from .models import Enterprise, Recruitment

class EnterpriseSerializer(serializers.ModelSerializer):
    """企业信息序列化器"""
    username = serializers.CharField(source="user.username", read_only=True)  # 显示关联的用户名

    class Meta:
        model = Enterprise
        fields = [
            "id", "user", "username", "name", "logo", "description",
            "contact_person", "contact_phone", "contact_email", "address",
            "created_at", "updated_at"
        ]
        read_only_fields = ["user"]  # 用户只能关联自己，前端无需传递

class RecruitmentSerializer(serializers.ModelSerializer):
    """招聘信息序列化器"""
    enterprise_name = serializers.CharField(source="enterprise.name", read_only=True)  # 冗余显示企业名称
    enterprise_id = serializers.IntegerField(source="enterprise.id", read_only=True)

    class Meta:
        model = Recruitment
        fields = [
            "id", "enterprise", "enterprise_name", "enterprise_id",
            "title", "job", "work_location", "salary", "experience",
            "education", "job_desc", "job_require", "is_published",
            "created_at", "updated_at"
        ]
        read_only_fields = ["enterprise"]  # 自动关联当前企业，前端无需传递