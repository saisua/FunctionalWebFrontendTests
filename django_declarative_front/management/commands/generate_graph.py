"""
Management command to generate site-wide page/state/workflow graphs.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate site-wide page/state/workflow graphs from BaseView pages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--out',
            type=Path,
            default=None,
            help='Output path (default: {BASE_DIR}/generated/graphs/site.svg)',
        )
        parser.add_argument(
            '--fmt',
            choices=('svg', 'png', 'pdf', 'dot'),
            default=None,
            help='Override output format',
        )
        parser.add_argument(
            '--no-per-page',
            action='store_true',
            default=False,
            help='Skip generating individual per-page graphs',
        )

    def handle(self, *args, **options):
        from django_declarative_front.utils.view_graph import build_and_write

        base_dir = Path(settings.BASE_DIR)
        out_path = options['out'] or base_dir / 'generated' / 'graphs' / 'site.svg'
        fmt = options['fmt'] or out_path.suffix.lstrip('.') or 'svg'
        per_page = not options['no_per_page']

        self.stdout.write(f'Generating site graph to {out_path}...')

        try:
            path = build_and_write(out=out_path, fmt=fmt, per_page=per_page)
            self.stdout.write(self.style.SUCCESS(f'Successfully generated graph: {path}'))
        except FileNotFoundError as e:
            if 'dot' in str(e):
                self.stderr.write(self.style.ERROR(
                    'Error: Graphviz is not installed or not in PATH.\n'
                    'Please install Graphviz:\n'
                    '  - Ubuntu/Debian: sudo apt-get install graphviz\n'
                    '  - macOS: brew install graphviz\n'
                    '  - Windows: https://graphviz.org/download/\n'
                    'Or use --fmt=dot to generate DOT format without Graphviz.'
                ))
            else:
                self.stderr.write(self.style.ERROR(f'Error generating graph: {e}'))
            raise
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error generating graph: {e}'))
            raise
