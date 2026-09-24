def render(page):
	with page.footer:
		page.text("> ")
		page.tag("span", id="year")
		page.text(" MyApp • Built with responsive CSS")
