from __future__ import annotations
from typing import Callable, Any
from functools import partial
import logging
import json

from django.template import Template, Context
from django.conf import settings
from django.http import HttpResponse

from yattag import Doc, SimpleDoc


# TODO: Move to config
logger = logging.getLogger(__name__)


Tag = SimpleDoc.Tag


def page_view(view_fn: Callable[[], Page]) -> HttpResponse:
	def _page_view(*args, **kwargs) -> HttpResponse:
		page = view_fn()

		template = Template(
			'\n'.join(page._template_prefixes) + '\n' + page.render()
		)

		return HttpResponse(
			template.render(Context(kwargs))
		)

	return _page_view


class Page:
	doc: Doc

	html: Page._LazyTag
	head: Page._LazyTag
	body: Page._LazyTag

	_template_prefixes: list[str]

	pyscript_config: dict[str, Any]

	_open_tag: Page._LazyTag
	_current_tag: Page._LazyTag  # noqa: F821

	def __init__(self):
		self.doc = Doc()
		self._template_prefixes = list()
		self.pyscript_config = dict(
			files=dict(),
			packages=list(),
			js_modules=dict(),
		)
		self._lazy_html = Page._LazyTag(self)

		self.html = self.tag(
			"html",
			unique_tag=True,
			add_child=False,
		)
		self._current_tag = self.html
		self._open_tag = self._current_tag

		with self.html:
			self.head = self.tag("head", unique_tag=True)
			self.body = self.tag("body", unique_tag=True)

	def __enter__(self, *args, **kwargs):
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f"Page enter {self._current_tag}")
		self._open_tag = self._current_tag
		self._open_tag.__enter__(*args, **kwargs)

	def __exit__(self, *args, **kwargs):
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f"Page exit {self._current_tag}", end='')
		self._open_tag.__exit__(*args, **kwargs)
		self._open_tag = self._current_tag
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" -> {self._open_tag}")

	def tag(
		self,
		*args,
		tag_name: str | None = None,
		id: str | None = None,
		unique_tag: bool = False,
		add_child: bool = True,
		**kwargs
	) -> Page._LazyTag:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page tag {args} {kwargs}")
		if id is not None:
			kwargs['id'] = id

		tag = Page._LazyTag(self, *args, **kwargs)

		if add_child:
			self._current_tag.children.append(tag)

		self._set_attr_tag(
			tag,
			*args,
			tag_name=tag_name,
			unique_tag=unique_tag,
			**kwargs
		)

		return tag

	def stag(self, *args, id: str | None = None, **kwargs) -> None:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page stag {args} {kwargs}")
		if id is not None:
			kwargs['id'] = id

		stag = partial(self._stag, *args, **kwargs)

		self._current_tag.children.append(stag)

	def _stag(self, *args, **kwargs) -> None:
		with self.doc.tag(*args, **kwargs):
			pass

	def text(self, *args, id: str | None = None, **kwargs) -> None:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page text {args} {kwargs}")
		if id is not None:
			kwargs['id'] = id

		text = partial(self.doc.text, *args, **kwargs)

		self._current_tag.children.append(text)

	def asis(self, *args, **kwargs) -> None:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page asis {args} {kwargs}")

		asis = partial(self.doc.asis, *args, **kwargs)

		self._current_tag.children.append(asis)

	def add_pyscript_file(
		self,
		file_path: str,
		*,
		target_path: str = '',
		static: bool = False,
		run: bool = False,
	) -> None:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page add_pyscript_file {file_path} {target_path}")

		if static:
			file_path = f"/{settings.STATIC_URL.strip('/')}/{file_path.lstrip('/')}"
		else:
			file_path = f"/api/pyscript/get_file?path={file_path}"

		if run:
			self.stag("script", type="py", src=file_path)
		else:
			self.pyscript_config['files'][file_path] = target_path

	def _set_attr_tag(
		self,
		tag,
		/,
		*args,
		tag_name: str | None = None,
		id: str | None = None,
		unique_tag: bool = False,
		**kwargs
	):
		if id is not None:
			setattr(self, id, tag)
		elif unique_tag:
			if tag_name is None:
				tag_name = args[0]

			setattr(self, tag_name, tag)

	def _pre_render(self) -> None:
		if any(self.pyscript_config.values()):
			self.head\
				.tag("py-config", hidden=True)\
				.text(json.dumps(self.pyscript_config))

	def render(self) -> str:
		self._pre_render()

		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f"#\n#\n#\nrender {self.html}\n#\n#\n#")
		self.html.render(self.doc)

		return self.doc.getvalue()

	@property
	def children(self) -> list[Page._LazyTag]:
		return [self.html]

	class _LazyTag:
		page: Page

		_args: tuple | list
		_kwargs: dict

		children: list[Callable[[None], None] | Page._LazyTag]
		_prev_tag: Page._LazyTag

		def __init__(self, page: Page, *args, **kwargs):
			self.page = page

			self._args = args
			self._kwargs = kwargs

			self._prev_tag = None

			self.children = kwargs.get("children", list())

		def __enter__(self, *args, **kwargs):
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f"LazyTag enter {self}")
			self._prev_tag = self.page._current_tag
			self.page._current_tag = self
			return self

		def __exit__(self, *args, **kwargs):
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f"LazyTag exit {self} -> {self._prev_tag}")
			self.page._current_tag = self._prev_tag
			self._prev_tag = None

		def tag(self, *args, **kwargs) -> Page._LazyTag:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f" LazyTag tag {args} {kwargs}")
			with self:
				tag = self.page.tag(*args, **kwargs)

			Page._set_attr_tag(
				self,
				tag,
				*args,
				**kwargs
			)

			return tag

		def stag(self, *args, **kwargs) -> None:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f" LazyTag stag {args} {kwargs}")
			with self:
				self.page.stag(*args, **kwargs)

		def text(self, *args, id: str | None = None, **kwargs) -> None:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f" LazyTag text {args} {kwargs}")
			with self:
				self.page.text(*args, **kwargs)

		def asis(self, *args, **kwargs) -> None:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f" LazyTag asis {args} {kwargs}")
			with self:
				self.page.asis(*args, **kwargs)

		def add_pyscript_file(
			self,
			file_path: str,
			*,
			target_path: str = ''
		) -> None:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f" LazyTag add_pyscript_file {file_path}")
			with self:
				self.page.add_pyscript_file(file_path, target_path=target_path)

		def render(self, doc: Doc, *, depth: int = 1) -> None:
			if logger.isEnabledFor(logging.DEBUG):
				logger.debug(f"{'  ' * depth}{self} render {doc}")
			with doc.tag(*self._args, **self._kwargs):
				for child in self.children:
					if isinstance(child, Page._LazyTag):
						child.render(doc, depth=depth + 1)
					else:
						if logger.isEnabledFor(logging.DEBUG):
							logger.debug(f"{'  ' * depth} {child}")
						child()

		def __repr__(self) -> str:
			repr = list("LazyTag")

			if self._args:
				repr.append(f"({' '.join(self._args)}")
				if self._kwargs:
					repr.append(f"{' '.join(f'{k}={v}' for k, v in self._kwargs.items())})")
				else:
					repr.append(")")
			elif self._kwargs:
				repr.append(f"{{{' '.join(f'{k}={v}' for k, v in self._kwargs.items())}}}")

			return "".join(repr)
