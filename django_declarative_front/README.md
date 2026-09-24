# WebFunReflex

A Python web frontend framework with declarative syntax, state machines and workflow DAGs.

## Features

- **Declarative HTML building**: Build web pages using Python's declarative syntax
- **State machine integration**: Manage UI states with state machines
- **Workflow DAGs**: Process workflows with dependency graphs
- **Reactive elements**: Bind DOM elements to Python state
- **Pyscript integration**: Execute Python code in the browser
- **Django integration**: Works as a Django plugin

## Installation

```bash
pip install webfunreflex
```

Or install from source:

```bash
git clone https://github.com/your-username/webfunreflex.git
cd webfunreflex
pip install -e .
```

## Usage

### 1. Add to Django Settings

Add `webfunreflex` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'webfunreflex',
]
```

### 2. Include URLs

Include the URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('webfunreflex.urls')),
]
```

### 3. Create Your First Page

```python
from pathlib import Path
from webfunreflex.src.view import BaseView
from webfunreflex.src.state_machine.state_machine import State
from webfunreflex.src.declarative.fact import Fact
from webfunreflex.src.declarative.events import Callback
from webfunreflex.utils.docstr import Doc


@Doc("My first page using WebFunReflex")
class view(BaseView):
    class Meta:
        _endpoint = Path("my-page")
        _page = build_page()
    
    class Counter(Fact):
        count: int = 0
    
    class Enabled(State):
        initial = True
        increment = State.to_itself()
        
        @staticmethod
        async def increment(state: view, event):
            state.Counter.count += 1
    
    increment_event = Callback.click("incrementBtn").do(BaseView.increment)
```

### 4. Build the Page

```python
from webfunreflex.pages.base import render as base

def build_page():
    page = base()
    
    with page.content:
        with page.tag("main"):
            page.tag("h1").text("My Page")
            page.tag("button", id="incrementBtn").text("Increment")
            page.tag("span", id="counter", get="Counter.count").text("0")
    
    return page
```

## Architecture

The plugin provides:

- **`webfunreflex.src`**: Core framework code (views, state machines, declarative syntax)
- **`webfunreflex.components`**: Reusable UI components
- **`webfunreflex.pages`**: Base page templates and builders
- **`webfunreflex.utils`**: Utility functions and classes
- **`webfunreflex.urls`**: Django URL patterns
- **`webfunreflex.api`**: API endpoints for pyscript and other features

## Backward Compatibility

The plugin maintains backward compatibility with the original `fun_django_web` namespace:

```python
# These imports still work:
from fun_django_web.src.view import BaseView
from fun_django_web.src.state_machine.state_machine import State
from fun_django_web.pages.base import render as base

# But we recommend using the new namespace:
from webfunreflex.src.view import BaseView
from webfunreflex.src.state_machine.state_machine import State
from webfunreflex.pages.base import render as base
```

## Documentation

See the documentation for more details on how to use the framework.

## License

MIT License