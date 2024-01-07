from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, mail_admins, send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .filters import PostFilter, NewsFilter
from .forms import PostForm
from .models import Post, Category, Author, Appointment, CategorySubscribe, PostCategory

from NewsPaper.settings import DEFAULT_FROM_EMAIL

from django.core.cache import cache


class PostList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['qty_post'] = len(Post.objects.order_by('time_in').values('id'))
        context['categories'] = Category.objects.all()
        context['filterset'] = self.filterset
        context['isauthor'] = self._isauthor()
        return context

    def _isauthor(self):
        try:
            Author.objects.get(users=self.request.user)
            return True
        except Author.DoesNotExist:
            return False


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

    def get_category(self, **kwargs):
        self.object.post = PostCategory.objects.get(post_id=self.id)
        return PostCategory.objects.get(pk=id)

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно

        obj = cache.get(f'product-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'product-{self.kwargs["pk"]}', obj)

        return obj


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'postcreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = Author.objects.get(users=self.request.user)
        if 'post' in self.request.path:
            type_ = 'PST'
        elif 'news' in self.request.path:
            type_ = 'NWS'
        self.object.type = type_
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    template_name = 'postedit.html'
    form_class = PostForm
    model = Post

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'postdelete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('postlist')


class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'news.html'
    model = Post
    form_class = PostForm


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'appointment/make_appointment.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            category=request.POST['category']
        )
        appointment.save()

        # получаем наш html
        html_content = render_to_string(
            'appointment/appointment_created.html',
            {
                'appointment': appointment,
            }
        )

        # в конструкторе уже знакомые нам параметры, да? Называются правда немного по-другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'{appointment.category} {appointment.date.strftime("%Y-%m-%d")}',
            body='',  # это то же, что и message
            from_email='IrinaAbr1986@yandex.ru',
            to=['irina.abrosimova@live.com'],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "appointment/appointment_created.html")  # добавляем html

        mail_admins(
            subject=f'{appointment.category} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        msg.send()

        return redirect('appointment_created')


class CategoryPost(DetailView):
    model = Category
    template_name = 'categories/post_category.html'
    context_object_name = 'postcategory'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(category=kwargs['object'])
        return context


# Добавление категории:
class AddCategoryView(CreateView):
    model = Category
    template_name = 'categories/add_category.html'
    fields = '__all__'


# Список категорий:
class CategoryList(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'category'


# Функция позволяющая подписаться на категорию
@login_required
def subscribe_to_category(request, pk):
    current_user = request.user
    category = Category.objects.get(id=pk)
    category.subscriber.add(current_user)
    message = 'Вы подписаны на рассылку постов категории'
    send_mail(
        subject=current_user.username,
        message=f'{message} {category}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[current_user.email]
    )
    return render(request, 'subscribe.html', {'category': category, 'message': message})


@login_required
def unsubscribe(request, pk):
    current_user = request.user
    category = Category.objects.get(id=pk)
    category.subscriber.remove(current_user)
    message = 'Вы успешно отписались от рассылки новостей категории'
    send_mail(
        subject=current_user.username,
        message=f'{message} {category}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[current_user.email]
    )
    return render(request, 'unsubscribe.html', {'category': category, 'message': message})


class IndexView(TemplateView):
    template_name = 'posts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context
