import reflex as rx
from httpx import AsyncClient

from rxconfig import config

import plotly.graph_objects as go

from functional.event import mvu_event
from functional.check import mvu_check


MINIMUM = 0


class Test2(rx.State):
    d_count: int = 0
    count: int = 0
    enabled: bool = False
    _plotly_line_data: list[float] = []
    plotly_chart: go.Figure = go.Figure()

    @rx.event
    def increment(self):
        if self.enabled:
            self.count += 1
            self._update_plotly_chart()
        else:
            self.d_count += 1
            # self.d_count.set(self.d_count.get() + 1)
            # self.dirty_vars.add("d_count")
            # self._mark_dirty()
        print(f"Incremented {self._plotly_line_data=}")

    @rx.event
    def decrement(self):
        if self.count > MINIMUM:
            self.count -= 1
            self._update_plotly_chart()

    @rx.event
    async def enable(self):
        was_enabled = self.enabled

        self.enabled = True

        if not was_enabled:
            self.count += self.d_count
            self.d_count = 0
            self._update_plotly_chart()
            yield Test2.save_data

    @rx.event
    def disable(self):
        self.enabled = False

    @rx.event
    def apply(self):
        self.count += self.d_count
        self._update_plotly_chart()

    @rx.event
    async def reset_(self):
        self.count = 0
        self.d_count = 0
        self.enabled = False

    def __str__(self):
        return f"Test2 {self.d_count=} {self.count=} {self.enabled=}"

    @rx.event(background=True)
    async def load_data(self):
        print("Loading data")
        async with AsyncClient() as client:
            response = await client.get(
                f"{config.api_url}/api/test2/data",
                timeout=10,
            )
        print(f"Loaded {len(response.json())} data")
        async with self:
            self._plotly_line_data = list(response.json()) + self._plotly_line_data
            self.gen_plotly_chart()

    @rx.event(background=True)
    async def save_data(self):
        print("Saving data")
        async with AsyncClient() as client:
            await client.post(
                f"{config.api_url}/api/test2/data",
                json=self._plotly_line_data,
            )

    @rx.event
    def gen_plotly_chart(self) -> go.Figure:
        self.plotly_chart = go.Figure(
            data=[go.Scatter(y=self._plotly_line_data)],
            layout=go.Layout(
                title="Line Chart",
                xaxis=go.layout.XAxis(title="X"),
                yaxis=go.layout.YAxis(title="Y"),
            ),
        )

    def _update_plotly_chart(self):
        self._plotly_line_data.append(self.count)
        self.gen_plotly_chart()


@rx.page("/test2", on_load=Test2.load_data)
def test2() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        # rx.vstack(
        #     rx.heading(
        #         "Welcome to Test 2!",
        #         size="9",
        #     ),
        #     # rx.spacer(spacing="5", direction="vertical"),
        #     rx.vstack(
        #         rx.text(f"Count: {Test2.count} ({Test2.d_count})"),
        #         rx.text(f"Enabled: {Test2.enabled}"),
        #         rx.hstack(
        #             rx.button(
        #                 "Increment",
        #                 on_click=Test2.increment,
        #                 color_scheme="grass",
        #             ),
        #             rx.button(
        #                 "Decrement",
        #                 on_click=Test2.decrement,
        #                 color_scheme="ruby",
        #             ),
        #         ),
        #         rx.hstack(
        #             rx.button("Enable", on_click=Test2.enable),
        #             rx.button("Disable", on_click=Test2.disable),
        #         ),
        #         rx.button(
        #             "Reset",
        #             on_click=Test2.reset_,
        #             type="reset",
        #             variant="soft",
        #         ),
        #         align_items="center",
        #     ),
        #     spacing="5",
        #     align_items="center",
        #     justify="center",
        #     min_height="85vh",
        # ),
        # rx.hover_card(
        #     rx.skeleton(
        #         rx.plotly(
        #             data=Test2.plotly_chart,
        #         )
        #     ),
        # ),
    )
