from django.core.management.base import BaseCommand, CommandError

from NewsPaper.news.models import Category, Post


class Command(BaseCommand):
    help = 'Удаление всех новостей из какой-либо категории'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        self.stdout.readable()
        self.stdout.write(f'Do u really want to delete all posts from category {options["category"]}? yes/no')
        answer = input()

        if answer == 'yes':
            category = Category.objects.get(name=options['category'])
            Post.objects.filter(category=category).delete()
            self.stdout.write(self.style.SUCCESS(f'All posts from category {category.name} has been deleted successfully'))
            return

        self.stdout.write(self.style.ERROR('Access denied'))
