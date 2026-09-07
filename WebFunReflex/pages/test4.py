import os

import reflex as rx

from functional.statemachine import rxState, StateMachine

import statemachine as sm

from WebFunReflex.components.test4_page_0 import gen_page_0


MINIMUM = 0


class StepsMenuSM(StateMachine):
	rx_state: rx.State = None

	step_0: sm.State = sm.State(initial=True, value=0)
	step_1: sm.State = sm.State(value=1)
	step_2: sm.State = sm.State(value=2)
	step_3: sm.State = sm.State(value=3)

	_next: sm.state.TransitionList = (
		step_0.to(step_1)
		| step_1.to(step_2)  # noqa: W503
		| step_2.to(step_3)  # noqa: W503
	)
	_prev: sm.state.TransitionList = (
		step_1.to(step_0)
		| step_2.to(step_1)  # noqa: W503
		| step_3.to(step_2)  # noqa: W503
	)
	_home: sm.state.TransitionList = (
		step_1.to(step_0)  # noqa: W503
		| step_2.to(step_0)  # noqa: W503
		| step_3.to(step_0)  # noqa: W503
	)
	_skip: sm.state.TransitionList = (
		step_0.to(step_3)
		| step_1.to(step_3)  # noqa: W503
		| step_2.to(step_3)  # noqa: W503
	)


class Test4(rxState, rx.State):
	_menu_sm: StepsMenuSM = StepsMenuSM()

	@rx.var(cache=False)
	def step(self) -> int:
		return self._menu_sm.current_state_value

	@rx.event
	def graph(self):
		self._menu_sm._graph().write_png(
			os.path.join(
				os.path.dirname(__file__),
				f"{self.__class__.__name__}_{self._menu_sm.__class__.__name__}_graph.png"
			)
		)

	@rx.event
	def on_load(self):
		super().on_load()

	def __str__(self):
		return f"Test4 {self._menu_sm.current_state_value=}"


@rx.page("/test4", on_load=Test4.on_load)
def test4() -> rx.Component:
	page_0, page_0_state = gen_page_0(Test4)

	_pages = [
		page_0_state,
	]

	return rx.vstack(
		rx.box(
			rx.image(
				src="/favicon.ico",
				height="48px",
				alt="Logo",
				position="relative",
				left="2vw",
				top="0vh",
			),
			rx.color_mode.button(
				position="absolute",
				right="2vw",
				top="3vh",
			),
			rx.button(
				"G",
				on_click=Test4.graph,
				position="absolute",
				right="2vw",
				top="10vh",
			),
			background_color="tomato",
			width="100%",
			min_height="12vh",
			display="flex",
			align_items="center",
		),
		rx.flex(
			rx.container(
				rx.card(
					rx.text(
						f"Step {Test4.step}",
						font_size="24px",
						font_weight="bold",
						display="flex",
						flex_flow="row-reverse",
					),
					rx.separator(height="1px", background_color="gray"),
					rx.cond(
						Test4.step == 0,
						page_0,
					),
				),
				width="100%",
				height="100%",
			),
			direction="column",
			flex_grow=1,
			width="100%",
		),
		rx.flex(
			rx.separator(height="1px", background_color="gray"),
			rx.container(
				rx.card(
					rx.hstack(
						rx.button(
							"Previous",
							on_click=Test4.prev,
							disabled=Test4.step == 0,
						),
						rx.cond(
							Test4.step == 0,
							rx.button(
								"Skip",
								on_click=Test4.skip,
							),
						),
						rx.cond(
							Test4.step != 0,
							rx.button(
								"Home",
								on_click=Test4.home,
							),
						),
						rx.button(
							"Next",
							on_click=Test4.next,
							disabled=(
								(Test4.step == 3)
								# &
								# (not _pages[Test4.step - 1].finished)
							),
						),
						align="center",
						justify="between",
					),
				),
			),
			width="100%",
			direction="column",
		),
		width="100%",
		height="100vh",
		position="relative",
	)
