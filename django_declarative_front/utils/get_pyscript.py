import io
import sys
import requests
import tarfile
from pathlib import Path
import subprocess
import re

from django.conf import settings


INTERPRETER = "pyodide"

registry_urls = {
	'pyscript': 'https://registry.npmjs.org/@pyscript/core/latest',
}
interpreters = {
	'pyodide': 'https://registry.npmjs.org/pyodide/latest',
	'micropython': 'https://registry.npmjs.org/@micropython/micropython-webassembly-pyscript'
}
wheels = {
	'micropip': 'micropip'
}
registry_urls[INTERPRETER] = interpreters[INTERPRETER]


micropip_re = re.compile(r'(["\']file_name["\']\s*:\s*["\'])micropip-[^"\']+(["\'])')


try:
	STATIC_ROOT = settings.STATIC_ROOT
except Exception:
	from fun_django_web.settings import STATIC_ROOT


def _download_file(url: str) -> io.BytesIO:
	bytes_io = io.BytesIO()
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		for chunk in r.iter_content(chunk_size=8192):
			bytes_io.write(chunk)
	bytes_io.seek(0)
	return bytes_io


def _download_whls(packages: list[str], output_dir: Path):
	subprocess.run(
		[
			sys.executable,
			"-m",
			"pip",
			"download",
			"--only-binary=:all:",
			"--dest",
			str(output_dir),
			*packages,
		],
		check=True,
	)


def get_pyscript(
	project_name: str,
):
	for folder, registry_url in registry_urls.items():
		output_dir = Path("libs", folder)

		if output_dir.is_dir():
			print(f"Directory '{output_dir}' already exists. Skipping all steps.")
			continue

		output_dir.mkdir(parents=True, exist_ok=True)
		(output_dir / ".gitignore").write_text('*')

		try:
			response = requests.get(registry_url)
			response.raise_for_status()
			data = response.json()

			if 'dist' not in data:
				if 'versions' in data:
					data = data['versions']
					data = data[sorted(data.keys())[-1]]

			if 'dist' not in data:
				raise RuntimeError(f"'dist' folder not found in {folder}")

			tarball_url = data['dist']['tarball']

			print(f"Downloading {tarball_url}...")
			bytes_io = _download_file(tarball_url)
			print("Download complete.")
		except requests.exceptions.RequestException as e:
			print(f"Error during download: {e}")
			return

		print(f"Extracting to '{output_dir}'...")
		try:
			tar: tarfile.TarFile
			with tarfile.open(fileobj=bytes_io, mode='r:gz') as tar:
				tar.extractall(path=output_dir)
			print("Extraction complete.")
		except tarfile.TarError as e:
			print(f"Error during extraction: {e}")
			return

	pyodide_dir = Path(
		'libs', 'pyodide', 'package'
	)
	whl_output_dir = pyodide_dir / 'libs' / 'pyodide' / 'package'
	whl_output_dir.mkdir(parents=True, exist_ok=True)

	micropip_file = list(whl_output_dir.glob("micropip*.whl"))
	if True or not len(micropip_file):
		_download_whls(wheels.values(), whl_output_dir)

		micropip_file = next(whl_output_dir.glob("micropip*.whl"))

		print(micropip_file.name)

		pyodide_lock = pyodide_dir / 'pyodide-lock.json'
		pyodide_lock.write_text(
			micropip_re.sub(
				rf"\1{micropip_file.name}\2",
				pyodide_lock.read_text()
			)
		)


if __name__ == "__main__":
	# project_name = input("Enter the project name: ")
	project_name = "fun_django_web"
	get_pyscript(project_name=project_name)
