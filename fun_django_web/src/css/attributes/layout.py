from typing import Literal, Final, TypeAlias, Union

from fun_django_web.src.css.hint import HintCSS

from fun_django_web.src.css.values.screen_size import ScreenSizeCSS


class layout:
    class z_index(HintCSS):
        attribute: Final[str] = "z-index"
        hint: TypeAlias = ScreenSizeCSS.hint
    z = z_index

    class gap(HintCSS):
        attribute: Final[str] = 'gap'
        hint: TypeAlias = Union[
            ScreenSizeCSS.hint,
            tuple[
                ScreenSizeCSS.hint,
                ScreenSizeCSS.hint,
            ],
            Literal[
                'initial',
                'inherit'
            ],
        ]

    class display(HintCSS):
        attribute: Final[str] = "display"
        hint: TypeAlias = Literal[
            "block",
            "inline",
            "inline-block",
            "flex",
            "grid",
            "none",
            "contents"
        ]

        class grid(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "grid",
                "inline-grid"
            ]

        class flex(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "flex",
                "inline-flex",
            ]

            class direction(HintCSS):
                attribute: Final[str] = "flex-direction"
                hint: TypeAlias = Literal[
                    "row",
                    "row-reverse",
                    "column",
                    "column-reverse",
                    "initial",
                    "inherit",
                ]

            class flex(HintCSS):
                attribute: Final[str] = "flex"
                hint: TypeAlias = Literal[
                    0,
                    1,
                    '0',
                    '1',
                    "auto",
                ]

            class wrap(HintCSS):
                attribute: Final[str] = "flex-wrap"
                hint: TypeAlias = Literal[
                    "nowrap",
                    "wrap",
                    "wrap-reverse",
                    "initial",
                    "inherit",
                ]

        class block(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "block",
                "inline-block",
            ]

    class align(HintCSS):
        attribute: Final[str] = "align-self"
        hint: TypeAlias = Literal[
            "auto",
            "stretch",
            "center",
            "flex-start",
            "flex-end",
            "baseline",
            "initial",
            "inherit"
        ]

        class content(HintCSS):
            attribute: Final[str] = "align-content"
            hint: TypeAlias = Literal[
                "stretch",
                "center",
                "flex-start",
                "flex-end",
                "space-between",
                "space-around",
                "space-evenly",
                "initial",
                "inherit"
            ]

        class children(HintCSS):
            attribute: Final[str] = "align-items"
            hint: TypeAlias = Literal[
                "normal",
                "stretch",
                "center",
                "start",
                "end",
                "flex-start",
                "flex-end",
                "baseline",
                "initial",
                "inherit"
            ]

        class text(HintCSS):
            attribute: Final[str] = "text-align"
            hint: TypeAlias = Literal[
                "left",
                "right",
                "center",
                "justify",
                "initial",
                "inherit",
            ]

    class justify(HintCSS):
        attribute: Final[str] = "justify-self"
        hint: TypeAlias = Literal[
            "auto",
            "normal",
            "stretch",
            "start",
            "left",
            "center",
            "end",
            "right",
            "safe",
            "unsafe",
            "initial",
            "inherit"
        ]

        class content(HintCSS):
            attribute: Final[str] = "justify-content"
            hint: TypeAlias = Literal[
                "stretch",
                "center",
                "flex-start",
                "flex-end",
                "space-between",
                "space-around",
                "space-evenly",
                "initial",
                "inherit"
            ]

        class children(HintCSS):
            attribute: Final[str] = "justify-items"
            hint: TypeAlias = Literal[
                "normal",
                "stretch",
                "center",
                "start",
                "end",
                "flex-start",
                "flex-end",
                "baseline",
                "initial",
                "inherit"
            ]
