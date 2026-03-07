"""
详细测试关注逻辑
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from register.models import User
from user_info.models import Follow

print("📊 关注关系详细分析")
print("=" * 80)

# 清除所有关注关系
Follow.objects.all().delete()
print("🗑️ 已清除所有关注关系\n")

# 获取测试用户
try:
    user1 = User.objects.get(username='userlzp')
    user2 = User.objects.get(username='userlzp2')
    
    print(f"测试用户:")
    print(f"  - user1: {user1.username} (ID: {user1.id})")
    print(f"  - user2: {user2.username} (ID: {user2.id})")
    print()
    
    # user1 关注 user2
    print("1️⃣ user1 关注 user2")
    follow = Follow.objects.create(follower=user1, following=user2)
    print(f"   创建关注关系: {follow}")
    print()
    
    # 检查数据库中的关注关系
    print("2️⃣ 数据库中的关注关系:")
    all_follows = Follow.objects.all()
    for f in all_follows:
        print(f"   - {f.follower.username} (follower) 关注了 {f.following.username} (following)")
    print()
    
    # 检查user1的统计
    print("3️⃣ user1的统计:")
    user1_followers = Follow.objects.filter(following=user1)
    user1_following = Follow.objects.filter(follower=user1)
    print(f"   - 粉丝数 (谁关注了user1): {user1_followers.count()}")
    print(f"   - 关注数 (user1关注了谁): {user1_following.count()}")
    if user1_following.exists():
        print(f"   - 关注列表: {[f.following.username for f in user1_following]}")
    print()
    
    # 检查user2的统计
    print("4️⃣ user2的统计:")
    user2_followers = Follow.objects.filter(following=user2)
    user2_following = Follow.objects.filter(follower=user2)
    print(f"   - 粉丝数 (谁关注了user2): {user2_followers.count()}")
    print(f"   - 关注数 (user2关注了谁): {user2_following.count()}")
    if user2_followers.exists():
        print(f"   - 粉丝列表: {[f.follower.username for f in user2_followers]}")
    print()
    
    # 验证后端API逻辑
    print("5️⃣ 验证后端API逻辑:")
    print(f"   user1的follower_count: {Follow.objects.filter(following=user1).count()}")
    print(f"   user1的following_count: {Follow.objects.filter(follower=user1).count()}")
    print(f"   user2的follower_count: {Follow.objects.filter(following=user2).count()}")
    print(f"   user2的following_count: {Follow.objects.filter(follower=user2).count()}")
    print()
    
    # 预期结果
    print("6️⃣ 预期结果:")
    print(f"   user1:")
    print(f"     - 粉丝数: 0 (没有人关注user1)")
    print(f"     - 关注数: 1 (user1关注了user2)")
    print(f"   user2:")
    print(f"     - 粉丝数: 1 (user1关注了user2)")
    print(f"     - 关注数: 0 (user2没有关注任何人)")
    print()
    
    # 取消关注
    print("7️⃣ user1 取消关注 user2")
    deleted_count, _ = Follow.objects.filter(follower=user1, following=user2).delete()
    print(f"   删除了 {deleted_count} 条关注关系")
    print()
    
    # 检查取消关注后的统计
    print("8️⃣ 取消关注后的统计:")
    print(f"   user1:")
    print(f"     - 粉丝数: {Follow.objects.filter(following=user1).count()}")
    print(f"     - 关注数: {Follow.objects.filter(follower=user1).count()}")
    print(f"   user2:")
    print(f"     - 粉丝数: {Follow.objects.filter(following=user2).count()}")
    print(f"     - 关注数: {Follow.objects.filter(follower=user2).count()}")
    
except User.DoesNotExist as e:
    print(f"❌ 用户不存在: {e}")
