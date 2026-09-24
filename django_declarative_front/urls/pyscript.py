"""
URL patterns for pyscript file serving.
"""

from django.urls import path
from django_declarative_front.api.pyscript.get_file import get_pyscript_file

app_name = 'pyscript'

urlpatterns = [
    path('get_file/', get_pyscript_file, name='get_pyscript_file'),
]