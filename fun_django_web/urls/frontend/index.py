from django.urls import path

from fun_django_web.pages.index import view as index_view


urlpatterns = [
	*index_view.get_urls(),
]
