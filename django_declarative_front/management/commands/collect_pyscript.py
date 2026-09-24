"""
Management command to collect pyscript files.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Collect pyscript files for the WebFunReflex framework'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Collecting pyscript files...'))
        # TODO: Implement pyscript file collection
        self.stdout.write(self.style.SUCCESS('Done.'))