from pathlib import Path

from fun_django_web.src.view import View

from .build_page import build_page
from .css import CSS


class view(View):
	_endpoint = Path("test3")
	_page = build_page()
	_stylesheets = CSS

	_test_data = "hello world attribute"

	def _test_back_method(self):
		return "hello world back method"

	def test_front_method(self):
		return "hello world front method"
