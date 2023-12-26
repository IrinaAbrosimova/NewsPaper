from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils.translation import pgettext_lazy


post = 'PST'
news = 'NWS'

TYPE = [
    (post, "Статья"),
    (news, "Новость")
]


class Author(models.Model):
    name = models.CharField(max_length=255)
    users = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = Post.objects.filter(author=self).aggregate(result=Sum('rating')).get('result')
        comment_rating = Comment.objects.filter(user=self.users).aggregate(result=Sum('rating')).get('result')
        posts_comment_rating = Comment.objects.filter(post__author__users=self.users).aggregate(result=Sum('rating')).get('result')
        self.user_rating = 3 * int(posts_rating) + int(comment_rating) + int(posts_comment_rating)
        self.save()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    subscriber = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return self.name.title()


class CategorySubscribe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=pgettext_lazy('category', 'category'))
    subscriber = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=pgettext_lazy('subscriber', 'subscriber'))


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name=pgettext_lazy('Author', 'Author'))
    type = models.CharField(max_length=7, choices=TYPE, default='NWS')
    time_in = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        text = self.text[:124]
        if len(self.text) > 124:
            text += '...'
        return text
        save()

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return self.text.text()


class Appointment(models.Model):
    date = models.DateField(
        default=datetime.utcnow,
    )
    client_name = models.CharField(
        max_length=200
    )
    message = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'
