from django.urls import path

from fun_django_web.api.pyscript.get_file import get_pyscript_file

urlpatterns = [
    path('get_file/', get_pyscript_file, name='get_pyscript_file'),
]
