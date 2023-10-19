from datetime import datetime

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .filters import PostFilter
from .forms import PostForm
from .models import Post


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['qty_post'] = len(Post.objects.order_by('time_in').values('id'))
        context['filterset'] = self.filterset
        return context


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-time_in']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()


class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'postcreate.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        print(post)
        if 'news' in self.request.path:
            post_type = 'NWS'
        elif 'post' in self.request.path:
            post_type = 'PST'
        post.type = post_type
        post.save()
        return super().form_valid(form)


class PostUpdate(UpdateView):
    template_name = 'postcreate.html'
    context_object_name = 'edit'
    form_class = PostForm
    model = Post

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView):
    model = Post
    template_name = 'postdelete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('postlist')
