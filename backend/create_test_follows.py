"""
创建测试关注关系数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from user_info.models import Follow

# 获取用户
try:
    user1 = User.objects.get(username='userlzp')
    user2 = User.objects.get(username='userlzp2')
    admin = User.objects.get(username='admin')
    
    print(f"✅ 找到用户:")
    print(f"  - {user1.username} (ID: {user1.id})")
    print(f"  - {user2.username} (ID: {user2.id})")
    print(f"  - {admin.username} (ID: {admin.id})")
    
    # 清除现有的关注关系
    Follow.objects.all().delete()
    print(f"\n🗑️ 清除现有的关注关系")
    
    # 创建关注关系
    # user1 关注 admin
    Follow.objects.create(follower=user1, following=admin)
    print(f"✅ {user1.username} 关注了 {admin.username}")
    
    # user2 关注 admin
    Follow.objects.create(follower=user2, following=admin)
    print(f"✅ {user2.username} 关注了 {admin.username}")
    
    # admin 关注 user1
    Follow.objects.create(follower=admin, following=user1)
    print(f"✅ {admin.username} 关注了 {user1.username}")
    
    # user1 关注 user2
    Follow.objects.create(follower=user1, following=user2)
    print(f"✅ {user1.username} 关注了 {user2.username}")
    
    print(f"\n📊 统计信息:")
    print(f"  - admin的粉丝数: {Follow.objects.filter(following=admin).count()}")
    print(f"  - admin的关注数: {Follow.objects.filter(follower=admin).count()}")
    print(f"  - user1的粉丝数: {Follow.objects.filter(following=user1).count()}")
    print(f"  - user1的关注数: {Follow.objects.filter(follower=user1).count()}")
    print(f"  - user2的粉丝数: {Follow.objects.filter(following=user2).count()}")
    print(f"  - user2的关注数: {Follow.objects.filter(follower=user2).count()}")
    
    print(f"\n🎉 测试数据创建完成！")
    
except User.DoesNotExist as e:
    print(f"❌ 用户不存在: {e}")
