import os

from django_declarative_front import BaseView
from .build_page import build_page


class view(BaseView):
	_endpoint = "/"
	_page = build_page()
