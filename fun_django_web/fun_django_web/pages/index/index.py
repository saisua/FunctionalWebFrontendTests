import os

from fun_django_web.src.page.page import page_view
from fun_django_web.pages.base import render as base


@page_view
def render():
	page = base()

	with page.content:
		with page.tag("main", klass="app-main main-card", id="mainContent"):
			page.tag("h1").text("Index")

			for folder in sorted(os.listdir("fun_django_web/pages")):
				match folder:
					case "index" | "base":
						continue
					case _ if folder.startswith("__"):
						continue
					case _:
						if os.path.isdir(f"fun_django_web/pages/{folder}"):
							page.tag("a", href=f"/{folder}", klass="btn btn-primary").text(folder)

	return page
