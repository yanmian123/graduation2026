import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from enterprise.models import Enterprise

def create_missing_enterprise_profile():
    """为缺少企业档案的用户创建企业档案"""
    
    # 找到缺少企业档案的企业用户
    user = User.objects.get(id=35, is_enterprise=True)
    
    print(f"为用户 {user.username} (ID: {user.id}) 创建企业档案...")
    
    # 检查是否已经有企业档案
    try:
        existing_enterprise = Enterprise.objects.get(user=user)
        print(f"⚠ 该用户已经有企业档案: {existing_enterprise.name}")
        return
    except Enterprise.DoesNotExist:
        pass
    
    # 创建企业档案
    enterprise = Enterprise.objects.create(
        user=user,
        name="测试企业",
        industry="互联网",
        scale="100-499人",
        description="这是一个测试企业档案",
        address="测试地址",
        contact_phone="13800138000",
        contact_email="test@example.com"
    )
    
    print(f"✓ 成功创建企业档案:")
    print(f"  - 企业名称: {enterprise.name}")
    print(f"  - 行业: {enterprise.industry}")
    print(f"  - 规模: {enterprise.scale}")
    print(f"  - 描述: {enterprise.description}")

if __name__ == "__main__":
    create_missing_enterprise_profile()
