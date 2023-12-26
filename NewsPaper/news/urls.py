from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, ProtectedView, AppointmentView, \
    AddCategoryView, CategoryList, CategoryPost, subscribe_to_category, IndexView
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', PostList.as_view(), name='postlist'),
    path('search/', PostSearch.as_view(), name='search'),
    path('create/', PostCreate.as_view(), name='newscreate'),
    path('post/create/', PostCreate.as_view(), name='postcreate'),
    path('<int:pk>/', cache_page(60*10)(PostDetail.as_view()), name='post'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='delete'),
    path('news/', ProtectedView.as_view(), name='news'),
    path('appointment_created/', AppointmentView.as_view(), name='appointment_created'),
    path('make_appointment/', AppointmentView.as_view(), name='make_appointment'),
    path('category/<int:pk>/', CategoryPost.as_view(), name='category'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('category_list/', CategoryList.as_view(), name='category_list'),
    path('category/<int:pk>/subscribe', subscribe_to_category),
    path('', IndexView.as_view()),

]
