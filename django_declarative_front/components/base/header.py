def render(page):
	with page.header:
		with page.tag("div", klass="brand"):
			page.tag("div", klass="logo", aria_hidden="true").text("A")
			with page.tag("div", klass="brand-text"):
				page.tag("div", style="font-weight:700").text("MyApp")
				page.tag(
					"div",
					klass="muted",
					style="font-size:0.8rem",
				).text("Small app subtitle")

		with page.tag("div", klass="header-actions"):
			page.tag("button", klass="btn", title="Notifications").text("🔔")
			page.tag("button", klass="btn", title="Account").text("👤")
