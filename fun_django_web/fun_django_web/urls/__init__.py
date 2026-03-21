from django.contrib import admin
from django.urls import path, include

from .frontend import urlpatterns as frontend_urlpatterns
from .backend import urlpatterns as backend_urlpatterns


urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/', include(backend_urlpatterns)),
	*frontend_urlpatterns,
]
