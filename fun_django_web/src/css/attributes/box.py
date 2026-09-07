from typing import Literal, Final, TypeAlias, Union

from fun_django_web.src.css.values.screen_size import ScreenSizeCSS
from fun_django_web.src.css.hint import HintCSS


class box:
    class width(HintCSS):
        attribute: Final[str] = "width"
        hint: TypeAlias = ScreenSizeCSS.hint

        class min(HintCSS):
            attribute: Final[str] = "min-width"
            hint: TypeAlias = ScreenSizeCSS.hint

        class max(HintCSS):
            attribute: Final[str] = "max-attribute"
            hint: TypeAlias = ScreenSizeCSS.hint

    class height(HintCSS):
        attribute: Final[str] = "height"
        hint: TypeAlias = ScreenSizeCSS.hint

        class min(HintCSS):
            attribute: Final[str] = "min-height"
            hint: TypeAlias = ScreenSizeCSS.hint

        class max(HintCSS):
            attribute: Final[str] = "max-height"
            hint: TypeAlias = ScreenSizeCSS.hint

    class margin(HintCSS):
        attribute: Final[str] = "margin"
        hint: TypeAlias = Union[
            ScreenSizeCSS.hint,
            tuple[
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint
            ]
        ]

        class top(HintCSS):
            attribute: Final[str] = "margin-top"
            hint: TypeAlias = ScreenSizeCSS.hint

        class bottom(HintCSS):
            attribute: Final[str] = "margin-bottom"
            hint: TypeAlias = ScreenSizeCSS.hint

        class right(HintCSS):
            attribute: Final[str] = "margin-right"
            hint: TypeAlias = ScreenSizeCSS.hint

        class left(HintCSS):
            attribute: Final[str] = "margin-left"
            hint: TypeAlias = ScreenSizeCSS.hint

    class padding(HintCSS):
        attribute: Final[str] = "padding"
        hint: TypeAlias = Union[
            ScreenSizeCSS.hint,
            tuple[
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint
            ]
        ]

        class top(HintCSS):
            attribute: Final[str] = "padding-top"
            hint: TypeAlias = ScreenSizeCSS.hint

        class bottom(HintCSS):
            attribute: Final[str] = "padding-bottom"
            hint: TypeAlias = ScreenSizeCSS.hint

        class right(HintCSS):
            attribute: Final[str] = "padding-right"
            hint: TypeAlias = ScreenSizeCSS.hint

        class left(HintCSS):
            attribute: Final[str] = "padding-left"
            hint: TypeAlias = ScreenSizeCSS.hint

    class sizing(HintCSS):
        attribute: Final[str] = "box-sizing"
        hint: TypeAlias = Literal[
            "border-box",
            "content-box",
        ]
