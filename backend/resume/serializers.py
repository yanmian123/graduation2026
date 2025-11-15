from rest_framework import serializers
from .models import Resume
from django.core.validators import RegexValidator

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        exclude = ['user'] 
        read_only_fields = ['id', 'created_at', 'updated_at', 'version']
    
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
        ],
        label="电话" 
    )
    
    def validate_skills(self, value):
        if value:
            # 处理：去重→去空格→重新拼接（如 "Python,  Vue, Python" → "Python,Vue"）
            skills_list = [skill.strip() for skill in value.split(',') if skill.strip()]
            return ','.join(list(set(skills_list)))
        return value
    
    #  自动填充当前登录用户（创建简历时）
    def create(self, validated_data):
        # 从上下文获取请求对象（需在视图中传递 context={'request': request}）
        user = self.context['request'].user
        return Resume.objects.create(user=user, **validated_data)