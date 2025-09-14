def render(page):
	with page.head:
		page.add_pyscript_file(
			'fun_django_web/components/loading/loading.pyscript.py',
			target_path='loading.py',
			run=True,
		)

	with page.body:
		with page.tag(
			"div",
			id="loading-overlay",
			klass="loading-overlay",
		):
			page.tag(
				"div",
				id="loading-spinner",
				klass="loading-spinner",
			)
