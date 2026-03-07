"""
创建测试关注关系并验证
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from user_info.models import Follow

print("📋 创建测试关注关系")
print("=" * 80)

# 清除所有关注关系
Follow.objects.all().delete()
print("🗑️ 已清除所有关注关系\n")

# 获取测试用户
user1 = User.objects.get(username='userlzp')
user2 = User.objects.get(username='userlzp2')

print(f"测试用户:")
print(f"  - user1: {user1.username} (ID: {user1.id})")
print(f"  - user2: {user2.username} (ID: {user2.id})")
print()

# user1 关注 user2
print("1️⃣ user1 关注 user2")
Follow.objects.create(follower=user1, following=user2)
print("✅ 关注关系创建成功\n")

# 检查统计
print("2️⃣ 统计结果:")
print(f"  user1:")
print(f"    - 粉丝数 (谁关注了user1): {Follow.objects.filter(following=user1).count()}")
print(f"    - 关注数 (user1关注了谁): {Follow.objects.filter(follower=user1).count()}")
print(f"  user2:")
print(f"    - 粉丝数 (谁关注了user2): {Follow.objects.filter(following=user2).count()}")
print(f"    - 关注数 (user2关注了谁): {Follow.objects.filter(follower=user2).count()}")
print()

print("3️⃣ 预期结果:")
print(f"  user1:")
print(f"    - 粉丝数: 0 (没有人关注user1)")
print(f"    - 关注数: 1 (user1关注了user2)")
print(f"  user2:")
print(f"    - 粉丝数: 1 (user1关注了user2)")
print(f"    - 关注数: 0 (user2没有关注任何人)")
print()

print("4️⃣ 前端显示:")
print(f"  user1的个人主页应该显示:")
print(f"    - 粉丝数: 0")
print(f"    - 关注数: 1")
print(f"  user2的个人主页应该显示:")
print(f"    - 粉丝数: 1")
print(f"    - 关注数: 0")
