"""
Management command to generate a new page.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate a new page for the WebFunReflex framework'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the page to generate')

    def handle(self, *args, **options):
        name = options['name']
        self.stdout.write(self.style.SUCCESS(f'Generating page: {name}'))
        # TODO: Implement page generation
        self.stdout.write(self.style.SUCCESS('Done.'))