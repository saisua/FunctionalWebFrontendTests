from django.urls import path

from fun_django_web.pages.index import render as index_render


urlpatterns = [
	path("", index_render, name="index"),
]
