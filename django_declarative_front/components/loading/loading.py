def render(page):
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
