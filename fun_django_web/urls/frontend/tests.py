from django.urls import path

from fun_django_web.pages.test import render as test_render
from fun_django_web.pages.test2 import render as test2_render
from fun_django_web.pages.test3 import view as test3_view
from fun_django_web.pages.test_solid import view as test_solid_view
from fun_django_web.pages.test_solid.callback import handle_solid_callback


urlpatterns = [
	path("test/", test_render, name="test"),
	path("test2/", test2_render, name="test2"),
	*test3_view.get_urls(),
	*test_solid_view.get_urls(),
	path("solid-callback/", handle_solid_callback, name="solid-callback"),
]
