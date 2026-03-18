from fun_django_web.src.page.page import page_view
from fun_django_web.pages.base import render as base


@page_view
def render():
    page = base()

    with page.content:
        with page.tag("main", klass="app-main main-card", id="mainContent"):
            page.tag("h1").text("Test 2")

    return page
