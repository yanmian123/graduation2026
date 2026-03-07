"""
检查数据库中的关注关系
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from user_info.models import Follow

print("📊 数据库中的关注关系:")
print("=" * 60)

# 显示所有关注关系
all_follows = Follow.objects.all().select_related('follower', 'following')
print(f"\n总共有 {all_follows.count()} 条关注关系:\n")

for follow in all_follows:
    print(f"  {follow.follower.username} (ID: {follow.follower.id}) 关注了 {follow.following.username} (ID: {follow.following.id})")

print("\n" + "=" * 60)
print("📋 各用户的统计信息:")
print("=" * 60)

# 统计每个用户的粉丝和关注
users = User.objects.all()
for user in users:
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    print(f"\n  {user.username} (ID: {user.id}):")
    print(f"    - 粉丝数: {follower_count}")
    print(f"    - 关注数: {following_count}")
