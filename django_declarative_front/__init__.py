"""
django_declarative_front - A Python web frontend framework with declarative syntax,
state machines and workflow DAGs.
"""

__version__ = "0.1.0"
__author__ = "WebFunReflex Contributors"

# Core classes - these are the most commonly used
from .view import BaseView, backend
from .state_machine.state_machine import State
from .declarative.fact import Fact
from .declarative.events import Callback
from .requests.request import Request
from .utils.docstr import Doc

# CSS classes
from .css.serializer import SerializerCSS
from .css.modules.display.flex import FlexCSS
from .css.components.notification import NotificationCSS
from .css.components.button import ButtonCSS

# Pages and components
from .templates.base import render as base_render
from .components.table.simple_table import simple_table

# Notifications
from .notifications.notifications import show_notification

# Export all for backward compatibility
__all__ = [
    # Core
    'BaseView',
    'backend',
    'State',
    'Fact',
    'Callback',
    'Request',
    'Doc',
    
    # CSS
    'SerializerCSS',
    'FlexCSS',
    'NotificationCSS',
    'ButtonCSS',
    
    # Pages and components
    'base_render',
    'simple_table',
    
    # Notifications
    'show_notification',
]
