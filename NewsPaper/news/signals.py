from NewsPaper.settings import SITE_URL, DEFAULT_FROM_EMAIL
import datetime
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import PostCategory, Post


def send_notifications(preview, pk, title, subscriber):
    html_content = render_to_string(
        'new_post_email.html',
        {
            'title': title,
            'text': preview,
            'link': f'{SITE_URL}{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=DEFAULT_FROM_EMAIL,
        to=subscriber
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


@receiver(pre_save, sender=Post)
def daily_posts_limit(sender, instance, **kwargs):
    user = instance.author.user
    today = datetime.datetime.now()
    count = Post.objects.filter(author__user=user, time_in__date=today).count()
    try:
        if count <= 3:
            pass
    except RuntimeError:
        print('Не допускается публиковать статьи более 3-х раз в день!')


@receiver(m2m_changed, sender=PostCategory)
def weekly_notify(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':

        categories = instance.category.all()
        subscribers_emails: list[str] = []
        for category in categories:
            subscribers_emails += category.subscriber.all()

        subscribers_emails = [s.email for s in subscribers_emails]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers_emails)
