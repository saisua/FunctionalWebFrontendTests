import inspect
from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod

from django.urls import path, URLPattern

from .method_endpoint import gen_method_endpoint
from .attribute_endpoint import gen_attr_endpoint
from .rpc_pending import add_rpc_pending
from .build_resources import gen_build_resources
from .base_endpoint import gen_base_endpoint


class View(ABC):
    _endpoint: Path

    _gen_urls: list[URLPattern] = list()
    _rpc_pending: list

    def __init__(self):
        self._rpc_pending = list()

    @abstractmethod
    def _build(self) -> Any:
        ...

    @classmethod
    def __init_subclass__(cls):
        # Checks
        if (
            not hasattr(cls, '_endpoint') or
            not isinstance(cls._endpoint, Path) or
            not str(cls._endpoint)
        ):
            raise ValueError("Invalid _endpoint")

        print(cls, "init subclass")

        # Generate endpoints for all '_*' methods
        for name, back_fn in inspect.getmembers(
            cls,
            predicate=inspect.isroutine
        ):
            if (
                not name.startswith('_') or
                name.startswith('__')
            ):
                continue

            cls._gen_urls.append(
                path(
                    str(cls._endpoint / name),
                    gen_method_endpoint(back_fn),
                )
            )

        # Generate endpoints for all '_*' attributed
        for back_attr in cls.__annotations__.keys():
            if back_attr.startswith('_'):
                continue
            cls._gen_urls.append(
                path(
                    str(cls._endpoint / back_attr),
                    gen_attr_endpoint(back_attr),
                )
            )

        # Generate methods that push rpc calls to the rpc DAG
        for name, front_fn in inspect.getmembers(
            cls,
            predicate=inspect.isroutine
        ):
            if name.startswith('_'):
                continue

            setattr(
                cls,
                f"_{name}",
                front_fn,
            )
            setattr(
                cls,
                name,
                add_rpc_pending(name),
            )

        # Generate a static script that builds the body
        gen_build_resources(cls)

        # Generate the base endpoint that returns an HTML with the specific
        # script, SSR data and sn empty body
        cls._gen_urls.append(
            path(
                str(cls._endpoint),
                gen_base_endpoint(cls),  # type: ignore
            )
        )

        cls.get_urls = View.get_urls

    @classmethod
    def get_urls(cls):
        return cls._gen_urls
