import reflex as rx


class Page0(rx.State):
	name: str = ""
	email: str = ""
	role: str = "user"
	terms_accepted: bool = False
	finished: bool = False

	@rx.var
	def can_submit(self) -> bool:
		return (
			bool(self.name)
			and bool(self.email)  # noqa: W503
			and bool(self.role)  # noqa: W503
			and bool(self.terms_accepted)  # noqa: W503
		)

	@rx.event
	def handle_submit(self, form_data: dict):
		print(form_data)
		self.name = form_data["name"]
		self.email = form_data["email"]
		self.role = form_data["role"]
		self.terms_accepted = form_data.get("terms", False) == "on"
		self.finished = True


def gen_page_0(test4: rx.State) -> tuple[rx.Component, rx.State]:
	return (
		rx.vstack(
			rx.heading("User Information Form", size="3"),
			rx.form(
				rx.vstack(
					rx.input(
						placeholder="Full Name",
						name="name",
						type="text",
						required=True,
					),
					rx.input(
						placeholder="Email",
						name="email",
						type="email",
						required=True,
					),
					rx.select(
						["user", "admin", "guest"],
						name="role",
						placeholder="Select your role",
						default_value="user",
					),
					rx.checkbox(
						"I accept the terms and conditions",
						name="terms",
					),
					rx.button(
						"Submit",
						type="submit",
						left_icon="check",
						disabled=~Page0.can_submit,
					),
					spacing="3",
				),
				on_submit=Page0.handle_submit,
			),
			rx.divider(),
			rx.cond(
				Page0.name,
				rx.vstack(
					rx.heading("Submitted Data", size="3"),
					rx.text(f"Name: {Page0.name}"),
					rx.text(f"Email: {Page0.email}"),
					rx.text(f"Role: {Page0.role}"),
					rx.text(f"Terms Accepted: {Page0.terms_accepted}"),
					spacing="2",
				),
			),
			spacing="4",
			width="100%",
			padding_top="5%",
		),
		Page0,
	)
