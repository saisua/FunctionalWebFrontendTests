# URLs package
from django.urls import path, include

app_name = 'django_declarative_front'

urlpatterns = [
    path('api/pyscript/', include('django_declarative_front.urls.pyscript', namespace='pyscript')),
    path('api/view/', include('django_declarative_front.urls.view', namespace='view')),
]