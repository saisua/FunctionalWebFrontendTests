from django.core.exceptions import ImproperlyConfigured


__version__ = "0.1.0"
__author__ = "WebFunReflex Contributors"


from .view import BaseView, backend


from .css.serializer import SerializerCSS
from .css.modules.display.flex import FlexCSS
from .css.components.notification import NotificationCSS
from .css.components.button import ButtonCSS

from .templates.base import render as base_render
from .components.table.simple_table import simple_table

from .static.state_machine.state_machine import State
from .static.declarative.fact import Fact
from .static.declarative.events import Callback
from .static.notifications.notifications import show_notification
from .static.requests.request import Request
from .static.utils.docstr import Doc


__all__ = [
    'BaseView',
    'backend',
    'State',
    'Fact',
    'Callback',
    'Request',
    'Doc',
    'SerializerCSS',
    'FlexCSS',
    'NotificationCSS',
    'ButtonCSS',
    'base_render',
    'simple_table',
    'show_notification',
]
