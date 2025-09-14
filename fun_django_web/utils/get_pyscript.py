import os
import io
import requests
import tarfile
from pathlib import Path


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
	output_dir: str = "./{project_name}/static/pyscript"
):
	registry_url = 'https://registry.npmjs.org/@pyscript/core/latest'

	output_dir = Path(
		f"./{output_dir.format(project_name=project_name).lstrip('./')}"
	)

	if os.path.exists(output_dir):
		print(f"Directory '{output_dir}' already exists. Skipping all steps.")
		return

	try:
		print("Fetching latest version information...")
		response = requests.get(registry_url)
		response.raise_for_status()
		data = response.json()
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
			members = list()
			for member in tar.getmembers():
				print(member.name)
				if (
					member.name.startswith('package/dist/')
					and member.name.endswith('.js')  # noqa: W503
					or member.name.endswith('.js.map')  # noqa: W503
				):
					member.name = os.path.basename(member.name)
					members.append(member)
			tar.extractall(path=output_dir, members=members)
		print("Extraction complete.")
	except tarfile.TarError as e:
		print(f"Error during extraction: {e}")


if __name__ == "__main__":
	# project_name = input("Enter the project name: ")
	project_name = "fun_django_web"
	get_pyscript(project_name=project_name)
