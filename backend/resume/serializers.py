from rest_framework import serializers
from .models import Resume
from django.core.validators import RegexValidator

class ResumeSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField() 
    class Meta:
        model = Resume
        exclude = ['user'] 
        read_only_fields = ['id', 'created_at', 'updated_at', 'version']
        # 添加pdf_url到可写字段
        extra_kwargs = {
            'pdf_url': {'required': False, 'allow_null': True,'read_only': False }
        }
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
    
    def get_pdf_url(self, obj):
        """返回完整的PDF文件URL"""
        if obj.pdf_url and hasattr(obj.pdf_url, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_url.url)
            else:
                # 如果是在某些上下文中没有request，返回相对路径
                return obj.pdf_url.url
        return None
    
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

    # 添加更新方法，处理PDF文件删除
    def update(self, instance, validated_data):
        # 如果pdf_url被设置为null，删除现有文件
        if 'pdf_url' in validated_data and validated_data['pdf_url'] is None:
            if instance.pdf_url:
                # 删除旧文件
                instance.pdf_url.delete(save=False)
        
        return super().update(instance, validated_data)
