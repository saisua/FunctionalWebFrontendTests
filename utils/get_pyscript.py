import io
import requests
import tarfile
from pathlib import Path


INTERPRETER = "pyodide"

registry_urls = {
	'pyscript': 'https://registry.npmjs.org/@pyscript/core/latest',
}
interpreters = {
	'pyodide': 'https://registry.npmjs.org/pyodide/latest',
	'micropython': 'https://registry.npmjs.org/@micropython/micropython-webassembly-pyscript'
}
registry_urls[INTERPRETER] = interpreters[INTERPRETER]


def _download_file(url: str) -> io.BytesIO:
	bytes_io = io.BytesIO()
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		for chunk in r.iter_content(chunk_size=8192):
			bytes_io.write(chunk)
	bytes_io.seek(0)
	return bytes_io


def get_pyscript(
	project_name: str,
):
	static_dir = Path(
		project_name, "static"
	)

	for folder, registry_url in registry_urls.items():
		output_dir = static_dir / folder

		if output_dir.is_dir():
			print(f"Directory '{output_dir}' already exists. Skipping all steps.")
			continue

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


if __name__ == "__main__":
	# project_name = input("Enter the project name: ")
	project_name = "fun_django_web"
	get_pyscript(project_name=project_name)
