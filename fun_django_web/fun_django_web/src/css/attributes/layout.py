from typing import Literal, Final, TypeAlias

from fun_django_web.src.css.attributes.hint import HintCSS


class layout:
    # @hint(
    #     Literal[
    #         "block",
    #         "inline",
    #         "inline-block",
    #         "flex",
    #         "grid",
    #         "none",
    #         "contents"
    #     ]
    # )
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

        # @hint(
        #     Literal[
        #         "grid",
        #         "inline-grid"
        #     ]
        # )
        class grid(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "grid",
                "inline-grid"
            ]

        # @hint(
        #     Literal[
        #         "flex",
        #         "inline-flex",
        #     ]
        # )
        class flex(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "flex",
                "inline-flex",
            ]

            # @hint(
            #     Literal[
            #         "row",
            #         "row-reverse",
            #         "column",
            #         "column-reverse",
            #         "initial",
            #         "inherit",
            #     ]
            # )
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

            # @hint(
            #     Literal[
            #         "nowrap",
            #         "wrap",
            #         "wrap-reverse",
            #         "initial",
            #         "inherit",
            #     ]
            # )
            class wrap(HintCSS):
                attribute: Final[str] = "flex-wrap"
                hint: TypeAlias = Literal[
                    "nowrap",
                    "wrap",
                    "wrap-reverse",
                    "initial",
                    "inherit",
                ]

        # @hint(
        #     Literal[
        #         "block",
        #         "inline-block",
        #     ]
        # )
        class block(HintCSS):
            attribute: Final[str] = "display"
            hint: TypeAlias = Literal[
                "block",
                "inline-block",
            ]
