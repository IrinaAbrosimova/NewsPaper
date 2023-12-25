import datetime

from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import PostCategory, Post
from django.conf import settings


def send_notifications(preview, pk, headline, subscribers):
    html_content = render_to_string(
        'new_post_email.html',
        {
            'headline': headline,
            'article_text': preview,
            'link': f'{settings.SITE_URL}posts/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject='Новая статья уже на сайте',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@receiver(pre_save, sender=Post)
def daily_posts_limit(sender, instance, **kwargs):
    user = instance.post_author.user
    today = datetime.datetime.now()
    count = Post.objects.filter(post_author__user=user, post_time__date=today).count()
    try:
        if count <= 3:
            pass
    except RuntimeError:
        print('Не допускается публиковать статьи более 3-х раз в день!')


@receiver(m2m_changed, sender=PostCategory)
def weekly_notify(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':

        categories = instance.post_category.all()
        subscribers_emails: list[str] = []
        for category in categories:
            subscribers_emails += category.subscribers.all()

        subscribers_emails = [s.email for s in subscribers_emails]

        send_notifications(instance.preview(), instance.pk, instance.headline, subscribers_emails)