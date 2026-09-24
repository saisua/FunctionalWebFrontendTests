"""
WebFunReflex settings for Django projects.

These settings can be overridden in your Django settings.py file.
"""

from django.conf import settings


# Default settings
DEFAULTS = {
    'WEBFUNREFLEX_PYSRIPT_FILES': {},
    'WEBFUNREFLEX_PYSRIPT_PACKAGES': [],
    'WEBFUNREFLEX_PYSRIPT_JS_MODULES': {},
    'WEBFUNREFLEX_STATIC_URL': 'static/',
    'WEBFUNREFLEX_COMPONENT_PATHS': [],
    'WEBFUNREFLEX_TEMPLATE_DIRS': [],
    'WEBFUNREFLEX_DEBUG': getattr(settings, 'DEBUG', False),
}


class WebFunReflexSettings:
    """Settings class for WebFunReflex framework."""
    
    def __getattr__(self, name):
        if name in DEFAULTS:
            return getattr(settings, name, DEFAULTS[name])
        raise AttributeError(f"Invalid setting: {name}")


# Global settings instance
webfunreflex_settings = WebFunReflexSettings()