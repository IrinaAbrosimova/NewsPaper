from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, ProtectedView

urlpatterns = [
    path('', PostList.as_view(), name='postlist'),
    path('search/', PostSearch.as_view(), name='search'),
    path('create/', PostCreate.as_view(), name='newscreate'),
    path('post/create/', PostCreate.as_view(), name='postcreate'),
    path('<int:pk>/', PostDetail.as_view(), name='post'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='delete'),
    path('news/', ProtectedView.as_view(), name = 'news'),
]
