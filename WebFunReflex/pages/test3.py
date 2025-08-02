from typing import Any
import os

import reflex as rx

from functional.statemachine import rxState, StateMachine

import statemachine as sm


MINIMUM = 0


@rx.serializer
def serialize_state(state: sm.State) -> Any:
	return state.value


class StateMachine(StateMachine):
	rx_state: rx.State = None

	enabled: sm.State = sm.State(value=False)
	disabled: sm.State = sm.State(initial=True, value=True)
	_count: sm.State = sm.State()
	_d_count: sm.State = sm.State()

	_enable: sm.state.TransitionList = (
		disabled.to(enabled)  # noqa: W503
		| _d_count.to(enabled)  # noqa: W503
	)
	_disable: sm.state.TransitionList = (
		enabled.to(disabled)
		| _count.to(disabled)  # noqa: W503
	)
	_increment: sm.state.TransitionList = (
		_count.to.itself()
		| enabled.to(_count)  # noqa: W503
		| disabled.to(_d_count)  # noqa: W503
		| _d_count.to.itself()  # noqa: W503
	)
	_decrement: sm.state.TransitionList = (
		_count.to.itself()
		| enabled.to(_count)  # noqa: W503
	)

	@_enable.on
	def on_enable(self):
		self.rx_state.count += self.rx_state.d_count
		self.rx_state.d_count = 0
		self.rx_state.enabled = True

	@_disable.on
	def on_disable(self):
		self.rx_state.enabled = False

	@_increment.on
	def on_increment(self):
		if self.rx_state.enabled:
			self.rx_state.count += 1
		else:
			self.rx_state.d_count += 1

	@_decrement.cond
	def check_decrement(self):
		return self.rx_state.enabled and self.rx_state.count > MINIMUM

	@_decrement.on
	def on_decrement(self):
		self.rx_state.count -= 1

	@_increment.after
	def after_increment(self):
		if self.rx_state.enabled and self.rx_state.count % 3 == 0:
			self._disable()


class Test3(rxState, rx.State):
	count: int = 0
	d_count: int = 0
	enabled: bool = False

	_sm: StateMachine = StateMachine()

	async def reset_(self):
		self.count = 0
		self.d_count = 0
		if self.enabled:
			self._sm._disable()

	@rx.event
	def graph(self):
		self._sm._graph().write_png(
			os.path.join(
				os.path.dirname(__file__),
				"test3_graph.png"
			)
		)

	@rx.event
	def on_load(self):
		super().on_load()

	def __str__(self):
		return f"Test3 {self.d_count=} {self.count=}"


@rx.page("/test3", on_load=Test3.on_load)
def test3() -> rx.Component:
	return rx.container(
		rx.color_mode.button(position="top-right"),
		rx.vstack(
			rx.heading(
				"Welcome to Test3!",
				size="9",
			),
			# rx.spacer(spacing="5", direction="vertical"),
			rx.vstack(
				rx.text(f"Count: {Test3.count} ({Test3.d_count})"),
				rx.text(f"Enabled: {Test3.enabled}"),
				rx.hstack(
					rx.button(
						"Increment",
						on_click=Test3.increment,
						color_scheme="grass",
					),
					rx.button(
						"Decrement",
						on_click=Test3.decrement,
						color_scheme="ruby",
					),
				),
				rx.hstack(
					rx.button("Enable", on_click=Test3.enable),
					rx.button("Disable", on_click=Test3.disable),
				),
				rx.button(
					"Reset",
					on_click=Test3.reset_,
					type="reset",
					variant="soft",
				),
				rx.button(
					"Graph",
					on_click=Test3.graph,
					color_scheme="purple",
				),
				align_items="center",
			),
			spacing="5",
			align_items="center",
			justify="center",
			min_height="85vh",
		),
	)
