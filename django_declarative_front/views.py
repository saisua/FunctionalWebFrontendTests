"""
Django views for WebFunReflex framework.

These views provide the backend for the framework's API endpoints.
"""

from django.http import HttpResponse


def index(request):
    """Main index view."""
    return HttpResponse("WebFunReflex Framework")