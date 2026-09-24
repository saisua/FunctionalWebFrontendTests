"""
Management command to generate autodocs using Sphinx.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate autodocs using Sphinx and copy to {BASE_DIR}/autodocs/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=Path,
            default=None,
            help='Output directory (default: {BASE_DIR}/autodocs/)',
        )
        parser.add_argument(
            '--docs-dir',
            type=Path,
            default=None,
            help='Source docs directory (default: {BASE_DIR}/docs/)',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            default=False,
            help='Clean build directory before generating',
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        output_dir = options['output_dir'] or base_dir / 'autodocs'
        docs_dir = options['docs_dir'] or base_dir / 'docs'
        clean = options['clean']

        if not docs_dir.exists():
            self.stderr.write(self.style.ERROR(f'Docs directory not found: {docs_dir}'))
            return

        build_dir = docs_dir / '_build'

        # Clean build directory if requested
        if clean and build_dir.exists():
            self.stdout.write(f'Cleaning build directory: {build_dir}')
            shutil.rmtree(build_dir)

        # Generate docs using Sphinx
        self.stdout.write('Generating documentation with Sphinx...')

        try:
            # Run Sphinx
            cmd = [
                sys.executable,
                '-m', 'sphinx',
                '-M', 'html',
                str(docs_dir),
                str(build_dir),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                if 'No module named sphinx' in result.stderr:
                    self.stderr.write(self.style.ERROR(
                        'Error: Sphinx is not installed.\n'
                        'Please install Sphinx:\n'
                        '  pip install sphinx sphinx-autodoc-annotation sphinx-rtd-theme\n'
                        'Or install the docs dependency group:\n'
                        '  uv sync --group docs'
                    ))
                else:
                    self.stderr.write(self.style.ERROR(f'Sphinx build failed:\n{result.stderr}'))
                return

            # Find the generated HTML directory
            html_dir = build_dir / 'html'
            if not html_dir.exists():
                self.stderr.write(self.style.ERROR(f'HTML output not found: {html_dir}'))
                return

            # Copy to output directory
            if output_dir.exists():
                self.stdout.write(f'Cleaning output directory: {output_dir}')
                shutil.rmtree(output_dir)

            self.stdout.write(f'Copying documentation to {output_dir}...')
            shutil.copytree(html_dir, output_dir)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully generated documentation to: {output_dir}'
            ))

        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f'Error running Sphinx: {e}'))
            raise
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error generating documentation: {e}'))
            raise
