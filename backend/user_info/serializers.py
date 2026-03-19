from rest_framework import serializers
from .models import VerificationApplication
from register.models import User
import os

class VerificationApplicationSerializer(serializers.ModelSerializer):
    """认证申请序列化器"""
    class Meta:
        model = VerificationApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by']


class VerificationApplicationCreateSerializer(serializers.ModelSerializer):
    """认证申请创建序列化器"""
    business_license = serializers.CharField(required=False, allow_null=True)
    student_card = serializers.CharField(required=False, allow_null=True)
    other_files = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    
    class Meta:
        model = VerificationApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by', 'status', 'user']
    
    def validate(self, attrs):
        verification_type = attrs.get('verification_type')
        
        # 企业认证需要营业执照
        if verification_type == 'ENTERPRISE':
            if not attrs.get('business_license'):
                raise serializers.ValidationError({
                    'business_license': '企业认证必须上传营业执照'
                })
        
        # 个人认证需要学信网截图
        if verification_type == 'INDIVIDUAL':
            if not attrs.get('student_card'):
                raise serializers.ValidationError({
                    'student_card': '个人认证必须上传学信网截图'
                })
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'sex', 'age', 'major', 
                  'phone_number', 'graduation_school', 'education_level', 'graduation_year',
                  'current_status', 'intended_position', 'intended_salary', 'address', 
                  'intended_city', 'personal_profile']
        read_only_fields = ['id', 'username']
