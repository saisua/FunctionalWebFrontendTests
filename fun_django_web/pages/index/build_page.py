from pathlib import Path

from django_declarative_front import base_render as base


def build_page():
	page = base()

	with page.content:
		with page.tag("main", klass="app-main main-card", id="mainContent"):
			page.tag("h1").text("Index")

			pages_dir = Path("fun_django_web/pages")
			for page_folder in sorted(pages_dir.iterdir()):
				if (
					not page_folder.is_dir() and
					not (page_folder / f"{page_folder.name}.py").exists()
				):
					continue

				match page_folder.name:
					case "index":
						continue
					case _ if page_folder.name.startswith("__"):
						continue
					case _:
						page.tag("a", href=f"{page_folder.name}/", klass="btn btn-primary").text(page_folder)

	return page
