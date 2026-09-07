from httpx import AsyncClient

import reflex as rx
from rxconfig import config


MINIMUM = 0


class Test5(rx.State):
    @rx.event
    async def success(self):
        async with AsyncClient() as client:
            response = await client.get(
                f"{config.api_url}/api/test5/success"
            )
        print(response.text)
        yield rx.toast(response.json()["status"])

    @rx.event
    async def fail(self):
        async with AsyncClient() as client:
            response = await client.get(
                f"{config.api_url}/api/test5/fail"
            )
        yield rx.toast(response.json()["status"])

    @rx.event
    async def cancel(self):
        async with AsyncClient() as client:
            response = await client.get(
                f"{config.api_url}/api/test5/cancel"
            )
        yield rx.toast(response.json()["status"])


@rx.page("/test5")
def test5() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading(
                "Welcome to Test5!",
                size="9",
            ),
            # rx.spacer(spacing="5", direction="vertical"),
            rx.vstack(
                rx.button("Success", on_click=Test5.success),
                rx.button("Fail", on_click=Test5.fail),
                rx.button("Cancel", on_click=Test5.cancel),
            ),
            spacing="5",
            align_items="center",
            justify="center",
            min_height="85vh",
        ),
    )
