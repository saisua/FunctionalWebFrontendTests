import os


def render(page):
	with page.head:
		page.add_pyscript_file(
			'fun_django_web/components/base/sidebar/sidebar.pyscript.py',
			target_path='sidebar.py',
			run=True,
		)

	with page.sidebar:
		with page.tag("nav"):
			with page.tag("a", href="/", klass="nav-link"):
				page.tag("span", klass="nav-icon").text("🏠")
				page.tag("span", klass="nav-text").text("Home")

		with page.tag(
			"div",
			style=(
				"margin-top:auto;"
				"display:flex;"
				"flex-direction:column;"
				"gap:0.5rem;"
				"align-items:center"
			),
		):
			page.tag(
				"button",
				id="collapseBtn",
				klass="btn",
				aria_pressed="false",
				title="Collapse sidebar",
			).text("<<")

			page.tag(
				"small",
				klass="muted"
			).text(f"v{os.environ.get('VERSION')}")
