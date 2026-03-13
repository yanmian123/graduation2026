from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()  # 获取自定义用户模型

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]  # 应用Django密码验证规则
    )
    password_confirm = serializers.CharField(write_only=True, required=True)  # 确认密码
    verification_code = serializers.CharField(write_only=True, required=False)  # 验证码（不保存到数据库）

    class Meta:
        model = User
        # 包含需要的字段（内置字段+自定义字段）
        fields = [ 
            'username','email', 'password', 'password_confirm','is_enterprise', 'verification_code'  # 按需添加其他字段
        ]
        extra_kwargs = {
            'username': {
                'error_messages': {
                    'unique': '用户名已被占用'
                }
            },
            'email': {
                'error_messages': {
                    'unique': '邮箱已被注册'
                }
            }
        }

    def validate(self, attrs):
        # 验证两次密码一致
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "两次密码输入不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # 移除确认密码字段
        validated_data.pop('verification_code', None)  # 移除验证码字段
        user = User.objects.create_user(**validated_data)  # 创建用户（自动加密密码）
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': '用户名或密码错误'
    }

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer