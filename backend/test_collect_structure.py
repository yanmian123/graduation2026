"""
测试收藏API - 检查返回数据结构
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graduation.settings')
django.setup()

from article_publish.models import Article, Collection
from register.models import User

print("📋 测试收藏API返回数据结构")
print("=" * 80)

# 获取测试用户
try:
    user = User.objects.get(username='userlzp')
    print(f"✅ 找到用户: {user.username} (ID: {user.id})")
except User.DoesNotExist:
    print("❌ 用户不存在")
    exit()

# 获取测试文章
try:
    article = Article.objects.first()
    if article:
        print(f"✅ 找到文章: {article.title} (ID: {article.id})")
        print(f"   作者: {article.user.username}")
        print(f"   当前收藏数: {article.star_count}")
    else:
        print("❌ 没有找到文章")
        exit()
except Exception as e:
    print(f"❌ 获取文章失败: {e}")
    exit()

# 检查收藏状态
collect_exists = Collection.objects.filter(user=user, article=article).exists()
print(f"\n当前收藏状态: {'已收藏' if collect_exists else '未收藏'}")

# 模拟收藏操作
print("\n" + "=" * 80)
print("模拟收藏操作:")
print("=" * 80)

if not collect_exists:
    print("\n1. 收藏文章...")
    Collection.objects.create(user=user, article=article)
    article.star_count += 1
    article.save()
    print(f"✅ 收藏成功")
    print(f"   收藏数更新为: {article.star_count}")
    print(f"   返回数据应该包含: {{'is_collected': True, 'count': {article.star_count}}}")
else:
    print("\n1. 取消收藏文章...")
    Collection.objects.filter(user=user, article=article).delete()
    article.star_count -= 1
    article.save()
    print(f"✅ 取消收藏成功")
    print(f"   收藏数更新为: {article.star_count}")
    print(f"   返回数据应该包含: {{'is_collected': False, 'count': {article.star_count}}}")

print("\n" + "=" * 80)
