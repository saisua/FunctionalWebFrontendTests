from typing import Literal, Final, TypeAlias

from css.screen_size import ScreenSizeCSS
from css.attributes.hint import HintCSS


class box:
    # @hint(ScreenSizeCSS)
    class width(HintCSS):
        attribute: Final[str] = "width"
        hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class min(HintCSS):
            attribute: Final[str] = "min-width"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class max(HintCSS):
            attribute: Final[str] = "max-attribute"
            hint: TypeAlias = ScreenSizeCSS

    # @hint(ScreenSizeCSS)
    class height(HintCSS):
        attribute: Final[str] = "height"
        hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class min(HintCSS):
            attribute: Final[str] = "min-height"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class max(HintCSS):
            attribute: Final[str] = "max-height"
            hint: TypeAlias = ScreenSizeCSS

    class margin(HintCSS):
        attribute: Final[str] = "margin"
        hint: TypeAlias = tuple[
            ScreenSizeCSS,
            ScreenSizeCSS,
            ScreenSizeCSS,
            ScreenSizeCSS
        ]

        # @hint(ScreenSizeCSS)
        class top(HintCSS):
            attribute: Final[str] = "margin-top"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class bottom(HintCSS):
            attribute: Final[str] = "margin-bottom"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class right(HintCSS):
            attribute: Final[str] = "margin-right"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class left(HintCSS):
            attribute: Final[str] = "margin-left"
            hint: TypeAlias = ScreenSizeCSS

    class padding(HintCSS):
        attribute: Final[str] = "padding"
        hint: TypeAlias = tuple[
            ScreenSizeCSS,
            ScreenSizeCSS,
            ScreenSizeCSS,
            ScreenSizeCSS
        ]

        # @hint(ScreenSizeCSS)
        class top(HintCSS):
            attribute: Final[str] = "padding-top"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class bottom(HintCSS):
            attribute: Final[str] = "padding-bottom"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class right(HintCSS):
            attribute: Final[str] = "padding-right"
            hint: TypeAlias = ScreenSizeCSS

        # @hint(ScreenSizeCSS)
        class left(HintCSS):
            attribute: Final[str] = "padding-left"
            hint: TypeAlias = ScreenSizeCSS

    # @hint(
    #     Literal[
    #         "border-box",
    #         "content-box",
    #     ]
    # )
    class sizing(HintCSS):
        attribute: Final[str] = "box-sizing"
        hint: TypeAlias = Literal[
            "border-box",
            "content-box",
        ]
