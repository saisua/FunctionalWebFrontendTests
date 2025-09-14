from django.urls import path, include

from .pyscript import urlpatterns as pyscript_urlpatterns


urlpatterns = [
	path('pyscript/', include(pyscript_urlpatterns)),
]
