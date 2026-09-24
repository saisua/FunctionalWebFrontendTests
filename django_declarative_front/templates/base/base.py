from typing import cast, Iterable

from django_declarative_front.page.page import Page

from django_declarative_front.components.base.header import render as render_header
from django_declarative_front.components.base.sidebar import render as render_sidebar  # noqa: E501
from django_declarative_front.components.base.footer import render as render_footer
from django_declarative_front.components.loading.loading import render as render_loading


class PageWithBasicStructure(Page):
	header: Page._LazyTag
	aside: Page._LazyTag
	content: Page._LazyTag
	footer: Page._LazyTag


def render(
	*args,
	title: str = "MyApp",
	python_packages: Iterable[str],
	icon: str = "{% static 'admin/img/icon-debug-dark.svg' %}",
	**kwargs
) -> PageWithBasicStructure:
	page = Page()

	page._template_prefixes.append("{% load static %}")
	page.add_pyscript_file(
		'state_machine/state_machine.py',
		static=True,
		target_path='state_machine.py',
		run=False,
	)
	page.add_pyscript_file(
		'workflows/workflows.py',
		static=True,
		target_path='workflows.py',
		run=False,
	)
	page.add_pyscript_file(
		'notifications/notifications.py',
		static=True,
		target_path='notifications.py',
		run=False,
	)
	page.pyscript_config['packages'].extend(python_packages)

	with page.head:
		page.stag("meta", charset="utf-8")
		page.stag(
			"meta",
			name="viewport",
			content="width=device-width,initial-scale=1",
		)
		page.tag("title").text(title)

		page.stag(
			"link",
			rel="icon",
			href=icon,
		)

		page.stag("link", rel="stylesheet", href="{% static 'admin/css/base.css' %}")

		page.stag(
			"script",
			type="module",
			src="{% static 'libs/pyscript/package/dist/core.js' %}"
		)

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

	return cast(PageWithBasicStructure, page)
