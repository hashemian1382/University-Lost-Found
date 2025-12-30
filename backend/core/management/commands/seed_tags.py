from django.core.management.base import BaseCommand
from core.models import Tag

class Command(BaseCommand):
    help = 'Seeds initial tags'

    def handle(self, *args, **kwargs):
        tags = ['Electronics', 'Books', 'Clothing', 'ID Cards', 'Keys', 'Wallet', 'Bags', 'Accessories', 'Other']
        for t in tags:
            Tag.objects.get_or_create(name=t)
        self.stdout.write(self.style.SUCCESS('Tags seeded successfully'))