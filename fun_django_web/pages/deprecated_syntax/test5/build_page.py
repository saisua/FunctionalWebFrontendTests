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
					id="counter_value",
					get="Counter.enabled",
				).text("0")

			with table.cell_1_0:
				page.tag(
					"span",
					id="dcounter",
				).text("DCounter: ")
				page.tag(
					"span",
					id="dcounter_value",
					get="Counter.disabled",
				).text("0")

			with table.cell_2_0:
				page.tag(
					"span",
					id="status_label",
				).text("Status: ")
				page.tag(
					"span",
					id="status_value",
					get="_current_state"
				).text("-")

			with table.cell_0_1:
				page.tag(
					"button",
					id="increment_btn",
					klass="btn btn-primary",
				).text("Increment")
			with table.cell_2_1:
				page.tag(
					"button",
					id="decrement_btn",
					klass="btn btn-primary",
				).text("Decrement")

			with table.cell_0_2:
				page.tag(
					"button",
					id="enable_btn",
					klass="btn btn-primary",
				).text("Enable")
			with table.cell_2_2:
				page.tag(
					"button",
					id="disable_btn",
					klass="btn btn-primary",
				).text("Disable")

			with table.cell_0_3:
				page.tag(
					"button",
					id="save_btn",
					klass="btn btn-primary",
				).text("Save")
			with table.cell_1_3:
				page.tag(
					"button",
					id="reset_btn",
					klass="btn btn-primary",
				).text("Reset")
			with table.cell_2_3:
				page.tag(
					"button",
					id="load_btn",
					klass="btn btn-primary",
					if_="Counter.enabled",
				).text("Load")

			with table.cell_0_4:
				page.tag(
					"span",
					id="last_saved",
				).text("Last saved")

			with table.cell_0_4:
				page.tag(
					"span",
					id="last_saved_time",
					get="last_saved_time",
				).text("Never")

			with table.cell_2_4:
				page.tag(
					"button",
					id="leave_btn",
					klass="btn btn-primary",
				).text("Leave")

	return page
