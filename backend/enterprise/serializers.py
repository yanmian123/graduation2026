from rest_framework import serializers
from .models import Enterprise, Recruitment, JobApplication
from resume.models import Resume 
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
    
    
# serializers.py
class JobApplicationSerializer(serializers.ModelSerializer):
    recruitment_title = serializers.CharField(source='recruitment.title', read_only=True)
    enterprise_name = serializers.CharField(source='recruitment.enterprise.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    pdf_file = serializers.FileField(read_only=True)
    # 显式声明字段
    recruitment = serializers.PrimaryKeyRelatedField(
        queryset=Recruitment.objects.all(),
        write_only=True
    )
    resume = serializers.PrimaryKeyRelatedField(
        queryset=Resume.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    status = serializers.ChoiceField(
        choices=JobApplication._meta.get_field('status').choices,
        default=JobApplication._meta.get_field('status').default,
        read_only=True  # 设为只读，由后端自动设置
    )
    
    # 快照字段
    resume_name = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    class Meta:
        model = JobApplication
        fields = [
            "id", "recruitment", "recruitment_title", "applicant", 
            "applicant_name", "resume", "resume_name", "status", 
            "applied_at", "enterprise_name", "resume_snapshot", "pdf_file",
            "education", "phone", "email"
        ]
        read_only_fields = ["applicant", "applied_at", "resume_snapshot", "pdf_file", "status"]
        
    def get_resume_name(self, obj):
        return obj.resume_snapshot.get('name', '简历快照')

    def get_education(self, obj):
        return obj.resume_snapshot.get('education', '未填写')

    def get_phone(self, obj):
        return obj.resume_snapshot.get('phone', '')

    def get_email(self, obj):
        return obj.resume_snapshot.get('email', '')
    
    def validate(self, attrs):
        """自定义验证逻辑"""
        if self.context['request'].method == 'POST':
            recruitment = attrs.get('recruitment')
            applicant = self.context['request'].user
            
            if recruitment and JobApplication.objects.filter(
                recruitment=recruitment, 
                applicant=applicant
            ).exists():
                raise serializers.ValidationError("您已经申请过该职位")
        
        return attrs