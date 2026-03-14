import inspect
from pathlib import Path
from abc import ABC, abstractmethod

from django.urls import path

from .method_endpoint import gen_method_endpoint
from .attribute_endpoint import gen_attr_endpoint
from .rpc_pending import add_rpc_pending
from .build_script import gen_build_script
from .base_endpoint import gen_base_endpoint


class View(ABC):
    _endpoint: Path

    _gen_urls = list()
    _rpc_pending: list

    @abstractmethod
    def _build(self):
        ...

    @classmethod
    def __subclasshook__(cls, child):
        # Checks
        if (
            not hasattr(child, '_endpoint') or
            not isinstance(child._endpoint, Path) or
            not str(child._endpoint)
        ):
            raise ValueError("Invalid _endpoint")

        # Generate endpoints for all '_*' methods
        for name, back_fn in inspect.getmembers(
            child,
            predicate=inspect.isroutine
        ):
            if (
                not name.startswith('_') or
                name.startswith('__')
            ):
                continue

            cls._gen_urls.append(
                path(
                    child.endpoint / name,
                    gen_method_endpoint(back_fn),
                )
            )

        # Generate endpoints for all '_*' attributed
        for back_attr in child.__annotations__.keys():
            if back_attr.startswith('_'):
                continue
            cls._gen_urls.append(
                path(
                    child.endpoint / back_attr,
                    gen_attr_endpoint(back_attr),
                )
            )

        # Generate methods that push rpc calls to the rpc DAG
        for name, front_fn in inspect.getmembers(
            child,
            predicate=inspect.isroutine
        ):
            if name.startswith('_'):
                continue

            setattr(
                child,
                f"_{name}",
                front_fn,
            )
            setattr(
                child,
                name,
                add_rpc_pending(name),
            )

        # Generate an endpoint that returns the script that builds the body
        cls._gen_urls.append(
            path(
                child.endpoint / "__script",
                gen_build_script(child),
            )
        )

        # Generate the base endpoint that returns an HTML with the specific
        # 
        # script, SSR data and sn empty body
        cls._gen_urls.append(
            path(
                child.endpoint,
                gen_base_endpoint(child),
            )
        )
        return True

    @classmethod
    def get_urls(cls):
        yield from cls._gen_urls
