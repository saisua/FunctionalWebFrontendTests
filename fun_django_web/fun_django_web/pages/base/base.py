from fun_django_web.src.page.page import Page

from fun_django_web.components.base.header import render as render_header
from fun_django_web.components.base.sidebar import render as render_sidebar  # noqa: E501
from fun_django_web.components.base.footer import render as render_footer
from fun_django_web.components.loading.loading import render as render_loading


def render(*args, **kwargs) -> Page:
	page = Page()

	page._template_prefixes.append("{% load static %}")
	page.add_pyscript_file(
		'py/state_machine.py',
		static=True,
		target_path='state_machine.py',
		run=False,
	)
	page.add_pyscript_file(
		'py/workflows.py',
		static=True,
		target_path='workflows.py',
		run=False,
	)
	page.add_pyscript_file(
		'py/notifications.py',
		static=True,
		target_path='notifications.py',
		run=False,
	)
	page.pyscript_config['packages'].extend([
		'python-statemachine',
		'aiofiles',
		'aiohttp',
		'dagio',
	])

	with page.head:
		page.stag("meta", charset="utf-8")
		page.stag(
			"meta",
			name="viewport",
			content="width=device-width,initial-scale=1",
		)
		page.tag("title").text("MyApp")

		page.stag("link", rel="icon", href="{% static 'img/favicon.ico' %}")

		page.stag("link", rel="stylesheet", href="{% static 'css/base.css' %}")

		page.stag("script", type="module", src="{% static 'pyscript/core.js' %}")

	with page.body:
		with page.tag("div", klass="app-wrap"):
			with page.tag("div", klass="layout"):
				page.tag("header", id="header", klass="app-header")

				page.tag(
					"aside",
					id="sidebar",
					klass="sidebar",
					role="navigation",
					aria_label="Main navigation",
				)

				with page.tag("div", klass="main-content"):
					page.tag("div", id='content', klass="content-area")

			page.tag("footer", id='footer', klass="app-footer")

	render_header(page)
	render_sidebar(page)
	render_footer(page)
	#
	render_loading(page)

	return page
