from rest_framework import serializers
from django.core.validators import RegexValidator 
from django.contrib.auth import get_user_model
# 获取自定义用户模型（对应你之前定义的 User 模型）
User=get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
    """用于查看用户信息的序列化器（只返回需要的字段）"""
    
    class Meta:
        model = User
        # 包含需要的字段（排除password等敏感信息）
        fields = [
            'id', 'username', 'nickname', 'sex', 'age', 
            'graduation_school', 'education_level', 'major', 
            'graduation_year', 'phone_number', 'current_status',
            'intended_position', 'intended_salary', 'address',
            'intended_city', 'personal_profile'
        ]
        read_only_fields = ['id', 'username']  # 只读字段

class UserInfoUpdateSerializer(serializers.ModelSerializer):
    """用于更新用户信息的序列化器(添加特定字段的验证)"""
    #手机号验证
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=15,
        help_text="手机号，允许为空",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="手机号格式不正确，必须为9到15位数字，可以包含国家代码"
            )
        ]
    )
    
    #自定义年龄验证
    age= serializers.IntegerField(
        required=False,
        min_value=0,
        max_value=120,
        help_text="年龄，必须在0到120之间"
    )
    
    graduation_year = serializers.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100,
        help_text="毕业年份，必须在1900到2100之间"
    )

    class Meta:
        model = User
        # 允许修改的字段（与查看序列化器一致，但可添加更多验证）
        fields = [
            'nickname', 'sex', 'age', 'graduation_school', 
            'education_level', 'major', 'graduation_year', 
            'phone_number', 'current_status', 'intended_position',
            'intended_salary', 'address', 'intended_city', 
            'personal_profile'
        ]