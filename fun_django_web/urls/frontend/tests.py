from django.urls import path


class fake_view:
	@staticmethod
	def get_urls(): return tuple()


from fun_django_web.pages.test import render as test_render
from fun_django_web.pages.test2 import render as test2_render
try:
	from fun_django_web.pages.test3 import view as test3_view
except Exception:
	test3_view = fake_view
try:
	from fun_django_web.pages.test4 import view as test4_view
except Exception:
	test4_view = fake_view
from fun_django_web.pages.test5 import view as test5_view


urlpatterns = [
	path("test/", test_render, name="test"),
	path("test2/", test2_render, name="test2"),
	*test3_view.get_urls(),
	*test4_view.get_urls(),
	*test5_view.get_urls(),
]
