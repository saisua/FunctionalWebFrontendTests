from django.urls import path


class fake_view:
	@staticmethod
	def get_urls(): return tuple()


from fun_django_web.pages.test5_lib import view as test5_lib_view


urlpatterns = [
	*test5_lib_view.get_urls(),
]
