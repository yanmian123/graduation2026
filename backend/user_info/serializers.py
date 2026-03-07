from rest_framework import serializers
from .models import VerificationApplication
from register.models import User

class VerificationApplicationSerializer(serializers.ModelSerializer):
    """认证申请序列化器"""
    class Meta:
        model = VerificationApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by']


class VerificationApplicationCreateSerializer(serializers.ModelSerializer):
    """认证申请创建序列化器"""
    class Meta:
        model = VerificationApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by', 'status']


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'sex', 'age', 'major', 
                  'phone_number', 'graduation_school', 'education_level', 'graduation_year',
                  'current_status', 'intended_position', 'intended_salary', 'address', 
                  'intended_city', 'personal_profile']
        read_only_fields = ['id', 'username']
