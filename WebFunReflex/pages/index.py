import os

import reflex as rx


@rx.page("/")
def index() -> rx.Component:
    py_files = [
        f[:-3] for f in os.listdir(os.path.dirname(__file__)) 
        if f.endswith('.py') and f != '__init__.py'
    ]

    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            *(
                rx.link(
                    rx.button(f"Start {i}"),
                    href=f"/{i}",
                )
                for i in py_files
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )
