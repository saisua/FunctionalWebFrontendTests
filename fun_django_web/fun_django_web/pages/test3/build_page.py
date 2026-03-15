from fun_django_web.pages.base import render as base
from fun_django_web.components.table.simple_table import simple_table


def build_page():
	page = base()

	with page.content:
		with page.tag("main", klass="app-main main-card", id="mainContent"):
			table = simple_table(
				page,
				rows=5,
				columns=3,
				headers=False,
			)

			with table.cell_0_0:
				page.tag(
					"span",
					id="counter",
				).text("Counter: ")
				page.tag(
					"span",
					id="counterValue",
				).text("0")

			with table.cell_1_0:
				page.tag(
					"span",
					id="dcounter",
				).text("DCounter: ")
				page.tag(
					"span",
					id="dcounterValue",
				).text("0")

			with table.cell_2_0:
				page.tag(
					"span",
					id="statusLabel",
				).text("Status: ")
				page.tag(
					"span",
					id="statusValue",
				).text("Disabled")

			with table.cell_0_1:
				page.tag(
					"button",
					id="incrementBtn",
					klass="btn btn-primary",
					# **{"py-click": "increment"},
				).text("Increment")
			with table.cell_2_1:
				page.tag(
					"button",
					id="decrementBtn",
					klass="btn btn-primary",
					# **{"py-click": "decrement"},
				).text("Decrement")

			with table.cell_0_2:
				page.tag(
					"button",
					id="enableBtn",
					klass="btn btn-primary",
					# **{"py-click": "enable"},
				).text("Enable")
			with table.cell_2_2:
				page.tag(
					"button",
					id="disableBtn",
					klass="btn btn-primary",
					# **{"py-click": "disable"},
				).text("Disable")

			with table.cell_0_3:
				page.tag(
					"button",
					id="saveBtn",
					klass="btn btn-primary",
					# **{"py-click": "save"},
				).text("Save")
			with table.cell_1_3:
				page.tag(
					"button",
					id="resetBtn",
					klass="btn btn-primary",
					# **{"py-click": "reset"},
				).text("Reset")
			with table.cell_2_3:
				page.tag(
					"button",
					id="loadBtn",
					klass="btn btn-primary",
					# **{"py-click": "load"},
				).text("Load")

			with table.cell_2_4:
				page.tag(
					"button",
					id="leaveBtn",
					klass="btn btn-primary",
					# **{"py-click": "leave"},
				).text("Leave")

	return page
