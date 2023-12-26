import datetime

from celery import shared_task
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category


@shared_task
def notify_about_new_post(pk):
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    subscribers: list[str] = []
    for category in categories:
        subscribers += category.subscriber.all()

    subscribers_emails = [s.email for s in subscribers]

    html_content = render_to_string(
        'new_post_email.html',
        {
            'title': post.title,
            'text': post.preview,
            'link': f'{settings.SITE_URL}news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject='Новая статья уже на сайте',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def weekly_mailing():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    this_week_posts = Post.objects.filter(time_in__gt=last_week)
    for category in Category.objects.all():
        post_list = this_week_posts.filter(category=category)
        if post_list:
            subscribers = category.subscriber.values('username', 'email')
            recipients = []
            for subscriber in subscribers:
                recipients.append(subscriber['email'])

            html_content = render_to_string(
                'news/daily_news.html',
                {
                    'link': f'{settings.SITE_URL}news/',
                }
            )

            msg = EmailMultiAlternatives(
                subject='Статьи за неделю',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
            )

            msg.attach_alternative(html_content, 'text/html')
            msg.send()

    print('Рассылка произведена!')
