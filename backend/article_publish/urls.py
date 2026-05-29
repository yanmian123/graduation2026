from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, FileUploadView,PostSearchView,CommentViewSet, UserViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'posts', ArticleViewSet, basename='article')#basename='article' 是为了在 URL 中使用 article 而不是 posts
router.register(r'comments', CommentViewSet, basename='comment')#basename='comment' 是为了在 URL 中使用 comment 而不是 comments
router.register(r'users', UserViewSet, basename='user')


urlpatterns = [
    path('posts/searching/', PostSearchView.as_view(), name='post-search'),
    path('', include(router.urls)),
    path('upload/file', FileUploadView.as_view(), name='file-upload'),
]

print("Article Publish 路由列表：")
for url in urlpatterns:
    print(url)