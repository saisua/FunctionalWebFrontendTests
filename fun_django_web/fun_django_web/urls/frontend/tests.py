from django.urls import path

from fun_django_web.pages.test import render as test_render
from fun_django_web.pages.test2 import render as test2_render


urlpatterns = [
	path("test/", test_render, name="test"),
	path("test2/", test2_render, name="test2"),
]
