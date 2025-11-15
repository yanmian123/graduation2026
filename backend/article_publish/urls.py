from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, FileUploadView,PostSearchView,CommentViewSet, UserViewSet

router = DefaultRouter()
router.register(r'posts', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('posts/searching/', PostSearchView.as_view(), name='post-search'),
    path('', include(router.urls)),
    path('upload/file', FileUploadView.as_view(), name='file-upload'),
]

print("Article Publish 路由列表：")
for url in urlpatterns:
    print(url)