from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete

urlpatterns = [
    path('', PostList.as_view(), name='postlist'),
    path('add/', PostCreate.as_view(), name='postcreate'),
    path('<int:pk>/', PostDetail.as_view(), name='post'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='postedit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='postdelete'),
]
