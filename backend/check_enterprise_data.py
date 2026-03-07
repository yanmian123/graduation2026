import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from enterprise.models import Enterprise

def find_users_without_enterprise_profile():
    """找出所有企业用户但没有企业档案的用户"""
    
    print("=== 检查企业用户和企业档案数据 ===\n")
    
    # 1. 查找所有标记为企业的用户
    enterprise_users = User.objects.filter(is_enterprise=True)
    print(f"标记为企业的用户总数: {enterprise_users.count()}")
    
    # 2. 查找所有有企业档案的用户
    enterprise_profiles = Enterprise.objects.all()
    print(f"有企业档案的用户总数: {enterprise_profiles.count()}")
    
    # 3. 找出没有企业档案的企业用户
    users_without_profile = []
    for user in enterprise_users:
        try:
            enterprise = Enterprise.objects.get(user=user)
            print(f"✓ 用户 {user.username} (ID: {user.id}) 有企业档案: {enterprise.name}")
        except Enterprise.DoesNotExist:
            users_without_profile.append(user)
            print(f"✗ 用户 {user.username} (ID: {user.id}) 没有企业档案")
    
    print(f"\n=== 总结 ===")
    print(f"缺少企业档案的企业用户数量: {len(users_without_profile)}")
    
    if users_without_profile:
        print("\n缺少企业档案的用户列表:")
        for user in users_without_profile:
            print(f"  - ID: {user.id}, 用户名: {user.username}, 昵称: {user.nickname}")
    
    # 4. 检查是否有企业档案但用户不是企业用户的情况
    print(f"\n=== 检查反向情况 ===")
    non_enterprise_with_profile = []
    for enterprise in enterprise_profiles:
        if not enterprise.user.is_enterprise:
            non_enterprise_with_profile.append(enterprise)
            print(f"⚠ 用户 {enterprise.user.username} (ID: {enterprise.user.id}) 有企业档案但标记为非企业用户")
    
    if non_enterprise_with_profile:
        print(f"\n有企业档案但标记为非企业用户的数量: {len(non_enterprise_with_profile)}")
    else:
        print("✓ 所有的企业档案都对应企业用户")

if __name__ == "__main__":
    find_users_without_enterprise_profile()
