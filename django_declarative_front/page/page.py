from __future__ import annotations
from typing import Callable, Any, Final, Self
from functools import partial
import logging
import json

from django.template import Template, Context
from django.conf import settings
from django.http import HttpResponse

from yattag import Doc, SimpleDoc

# TODO: Implement load PUGs
# TODO: Implement if/elif/else in webfunreflex/src/reactivity/reactive.py
# TODO: Resolve in SSR if/get values if they are solvable (backend only)
# TODO: Implement that get/if/elif/else work in SSR if all values are solvable

# TODO: Move to config
logger = logging.getLogger(__name__)


Tag = SimpleDoc.Tag


def page_view(view_fn: Callable[[], Page]) -> Callable[..., HttpResponse]:
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

	_builder_start: Final[list[str]] = [
		"from js import document",
		"body = document.getElementsByTagName('body')[0]",
		"parents = [body]",
	]
	_builder_diff_start: Final[list[str]] = [
		"from js import document",
	]
	_builder_kwarg_replacements: Final[dict[str, str]] = {
		'klass': 'class'
	}

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
			logger.debug(f"Page exit {self._current_tag}")
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
		run: bool = False,
	) -> None:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f" Page add_pyscript_file {file_path} {target_path}")

		file_path = f"/{settings.STATIC_URL.strip('/')}/{file_path.lstrip('/')}"

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
	) -> None:
		if id is not None:
			setattr(self, id, tag)
			setattr(tag, 'id', f"'#{id}'")
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

	def builder(self) -> list[str]:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f"#\n#\n#\nbuilder {self.html}\n#\n#\n#")
		return self.html.builder()

	def diff_builder(self, other: Page) -> list[str]:
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug(f"#\n#\n#\nbuilder {self.html}\n#\n#\n#")
		return self.html.diff_builder(other.html)

	@property
	def children(self) -> list[Page._LazyTag]:
		return [self.html]

	def add_packages(self, *packages: str) -> None:
		self.pyscript_config['packages'].extend(packages)

	class _LazyTag:
		page: Page

		id: str | None = None

		_args: tuple | list
		_kwargs: dict

		children: list[Callable[[None], None] | Page._LazyTag]
		_prev_tag: Page._LazyTag | None = None

		def __init__(self, page: Page, *args, **kwargs):
			self.page = page

			self._args = args
			self._kwargs = kwargs

			self.id = kwargs.get('id', None)
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

		def __eq__(self, value: object) -> bool:
			if not isinstance(value, type(self)):
				return False
			return (
				self.id == value.id and
				self._args == value._args and
				self._kwargs == value._kwargs
			)

		@property
		def tag_name(self):
			return self._args[0]

		@property
		def css_selector(self):
			return f"{self._args[0]}[{' '.join(f'{key}={value!r}' for key, value in self._kwargs)}]"

		@property
		def path(self):
			curr_tag: Page._LazyTag | None = self._prev_tag
			path: list[Page._LazyTag] = [self]

			while curr_tag is not None:
				path.insert(0, curr_tag)
				curr_tag = curr_tag._prev_tag

			return path

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

		def builder(self, output: list | None = None, *, depth: int = 1) -> list[str]:
			if output is None:
				output = Page._builder_start.copy()

			output.append(f"new_element = document.createElement('{self._args[0]}')")
			for kwarg, value in self._kwargs.items():
				kwarg = Page._builder_kwarg_replacements.get(kwarg, kwarg)

				output.append(f"new_element.setAttribute('{kwarg}', '{value}')")

			output.append("parents[-1].appendChild(new_element)")

			if self.children:
				output.append("parents.append(new_element)")

				for child in self.children:
					if isinstance(child, Page._LazyTag):
						child.builder(output=output, depth=depth + 1)
					elif isinstance(child, partial):
						if child.func.__qualname__ == "SimpleDoc.text":
							output.append(f"parents[-1].innerText = '{child.args[0]}'")
						elif child.func.__qualname__ == "SimpleDoc.asis":
							output.append(f"parents[-1].innerHTML = '{child.args[0]}'")
						else:
							raise NotImplementedError(child)

				output.append("parents.pop(-1)")

			return output

		def diff_builder(
			self,
			other_tag: Self,
			output: list | None = None,
			*,
			depth: int = 1,
			path_str: str | None = None
		) -> list[str]:
			if path_str is None:
				path_str = '>'.join(
					tag.tag_name
					for tag in self.path
				)

			if output is None:
				output = Page._builder_diff_start.copy()
				output.append(f"current_parent = document.querySelector('{path_str}')")
				output.append("parents = [current_parent]")  # Prolly unnecessary to add curr_par
				output.append("children_to_remove = list()")
				output.append("from time import sleep")
			# output.append(f"print(' '*{depth-1}, '{self.tag_name}')")
			# output.append("sleep(1)")

			pending_children: list[Page._LazyTag] = list()
			seen_tag_names: dict[str, int] = dict()

			mapped_children_index: int = 0
			n_removed_children: int = 0
			for other_child in other_tag.children:
				if isinstance(other_child, partial):
					output.append(
						"if current_parent and current_parent.childElementCount == 0: "
						f"current_parent.innerText = '{other_child.args[0]}'"
					)
					continue

				other_tag_name = other_child.tag_name
				for n_child, child in enumerate(self.children[mapped_children_index:], start=mapped_children_index):
					if isinstance(child, partial):
						continue
					child_tag_name = child.tag_name

					if other_tag_name == child_tag_name:
						for skipped_child_n in range(mapped_children_index, n_child):
							skipped_child_tag = self.children[skipped_child_n]
							if isinstance(skipped_child_tag, partial):
								continue
							nth_child = seen_tag_names.setdefault(skipped_child_tag.tag_name, 1)
							skip_child_qsel = f"{path_str}>{skipped_child_tag.tag_name}:nth-of-type({nth_child})"

							# output.append(
							# 	f"print(' '*{depth-1}, 'removed', document.querySelector('{skip_child_qsel}'))"
							# )
							output.append(f"document.querySelector('{skip_child_qsel}').remove()")
							n_removed_children += 1

						for pending_child in pending_children:
							pending_child.builder(output, depth=depth+1)
						pending_children.clear()

						output.append("parents.append(current_parent)")

						parent_path_str = f"{path_str}>{child_tag_name}"
						nth_child = seen_tag_names.setdefault(child_tag_name, 1)
						parent_path_str += f":nth-of-type({nth_child})"
						seen_tag_names[child_tag_name] += 1

						output.append(f"current_parent = document.querySelector('{parent_path_str}')")
						# output.append(f"print(' '*{depth}, 'new abs parent', current_parent, '{parent_path_str}')")

						for other_kw, other_val in other_child._kwargs.items():
							if child._kwargs.get(other_kw) != other_val:
								kwarg = Page._builder_kwarg_replacements.get(other_kw, other_kw)
								output.append(f"current_parent.setAttribute('{kwarg}', '{other_val}')")
						for child_kw in child._kwargs:
							if child_kw not in other_child._kwargs:
								output.append(f"current_parent.removeAttribute('{child_kw}')")

						child.diff_builder(other_child, output, depth=depth+1, path_str=parent_path_str)

						output.append("current_parent = parents.pop(-1)")

						mapped_children_index = n_child + 1
						break
				else:
					pending_children.append(other_child)

			# output.append("sleep(1)")

			for skipped_child_n in range(mapped_children_index, len(self.children)):
				skipped_child_tag = self.children[skipped_child_n]
				if isinstance(skipped_child_tag, partial):
					continue

				nth_child = seen_tag_names.setdefault(skipped_child_tag.tag_name, 1)
				skip_child_qsel = f"{path_str}>{skipped_child_tag.tag_name}:nth-of-type({nth_child})"

				# output.append(
				# 	f"print(' '*{depth-1}, 'removed', document.querySelector('{skip_child_qsel}'))"
				# )
				output.append(f"document.querySelector('{skip_child_qsel}').remove()")

				n_removed_children += 1
			for pending_child in pending_children:
				pending_child.builder(output, depth=depth+1)
			pending_children.clear()

			return output

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
