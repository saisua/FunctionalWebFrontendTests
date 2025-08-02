import reflex as rx

from .pages import *  # noqa: F401 F403
from .back_main import app as api


app = rx.App(
    theme=rx.theme(
        radius="medium",
        accent_color="teal",
        gray_color="olive",
        font_family="Inter",
    ),
    api_transformer=api,
)
