from pathlib import Path

from fun_django_web.src.view import View

from .build_page import build_page
from .css import CSS


class view(View):
	_endpoint = Path("test3")
	_page = build_page()
	_stylesheets = CSS

	test_data: str = "hello world attribute"

	counter: int = 0
	_disabled_counter: int = 0

	def _increment(self):
		self._disabled_counter += 1
		print(f"Count: {self.counter}")
	
	def increment(self):
		...

	def _test_back_method(self):
		self.test_front_method(event=None)
		return "hello world back method"

	def test_front_method(self, event):
		return print("hello world front method")
