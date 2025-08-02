import reflex as rx
from httpx import AsyncClient

from rxconfig import config

from functional.event import mvu_event
from functional.check import mvu_check


MINIMUM = 0


class Test(rx.State):
    d_count: int = 0
    count: int = 0
    enabled: bool = False

    @mvu_event(check_after="check_disable")
    def increment(self):
        if self.enabled:
            self.count += 1
        else:
            self.d_count += 1

    @mvu_event(
        check_before="check_warn_at_minimum",
        check_after="check_disable_at_minimum",
    )
    def decrement(self):
        if self.count > MINIMUM:
            self.count -= 1

    @mvu_event
    def warn_at_minimum(self):
        yield rx.toast(f"Count is at minimum: {MINIMUM}")

    @mvu_check(triggers="warn_at_minimum")
    def check_warn_at_minimum(self):
        return self.count == MINIMUM

    @mvu_event(
        check_before="check_warn_already_enabled",
        check_after="check_apply",
    )
    async def enable(self):
        self.enabled = True

    @mvu_event()
    async def disable(self):
        self.enabled = False

    @mvu_check(triggers="disable")
    def check_disable(self):
        return self.enabled and self.count % 3 == 0

    @mvu_check(triggers="disable")
    def check_disable_at_minimum(self):
        return self.enabled and self.count == MINIMUM

    @mvu_event(background=True)
    async def apply(self):
        async with self:
            self.count += self.d_count
            self.d_count = 0

    @mvu_check(triggers="apply")
    async def check_apply(self):
        return self.enabled and self.d_count

    @mvu_event
    async def warn_already_enabled(self):
        async with AsyncClient() as client:
            response = await client.get(
                f"{config.api_url}/test/Already enabled"
            )
        yield rx.toast(response.json()["message"])

    @mvu_event
    def not_warn_already_enabled(self):
        print("Enabled successfully")

    @mvu_check(
        triggers=["warn_already_enabled"],
        else_triggers=["not_warn_already_enabled"],
    )
    def check_warn_already_enabled(self):
        return self.enabled

    @mvu_event
    async def reset_(self):
        self.count = 0
        self.d_count = 0
        self.enabled = False

    def __str__(self):
        return f"Test {self.d_count=} {self.count=} {self.enabled=}"


@rx.page("/test")
def test() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading(
                "Welcome to Test!",
                size="9",
            ),
            # rx.spacer(spacing="5", direction="vertical"),
            rx.vstack(
                rx.text(f"Count: {Test.count} ({Test.d_count})"),
                rx.text(f"Enabled: {Test.enabled}"),
                rx.hstack(
                    rx.button(
                        "Increment",
                        on_click=Test.increment,
                        color_scheme="grass",
                    ),
                    rx.button(
                        "Decrement",
                        on_click=Test.decrement,
                        color_scheme="ruby",
                    ),
                ),
                rx.hstack(
                    rx.button("Enable", on_click=Test.enable),
                    rx.button("Disable", on_click=Test.disable),
                ),
                rx.button(
                    "Reset",
                    on_click=Test.reset_,
                    type="reset",
                    variant="soft",
                ),
                align_items="center",
            ),
            spacing="5",
            align_items="center",
            justify="center",
            min_height="85vh",
        ),
    )
