import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui, app
from config import config
from models.database import init_db

init_db()


@ui.page("/")
def index():
    ui.navigate.to("/dashboard")


@ui.page("/dashboard")
def dashboard_page():
    _layout("Dashboard")
    from pages.dashboard import render
    render()


@ui.page("/agents")
def agents_page():
    _layout("Agents")
    from pages.agents import render
    render()


@ui.page("/agencies")
def agencies_page():
    _layout("Agencies")
    from pages.agencies import render
    render()


@ui.page("/manuscripts")
def manuscripts_page():
    _layout("Manuscripts")
    from pages.manuscripts import render
    render()


@ui.page("/authors")
def authors_page():
    _layout("Authors")
    from pages.authors import render
    render()


@ui.page("/query-letters")
def query_letters_page():
    _layout("Query Letters")
    from pages.query_letters import render
    render()


@ui.page("/scraper")
def scraper_page():
    _layout("Scraper")
    from pages.scraper import render
    render()


def _layout(active: str):
    ui.colors(primary="#5c4f3d", secondary="#8a7e72", accent="#a08b70")

    with ui.header().classes("items-center justify-between"):
        ui.label("QueryForge v2").classes("text-h5 font-bold q-ml-md")

        pages = [
            ("Dashboard", "/dashboard"),
            ("Agents", "/agents"),
            ("Agencies", "/agencies"),
            ("Manuscripts", "/manuscripts"),
            ("Authors", "/authors"),
            ("Query Letters", "/query-letters"),
            ("Scraper", "/scraper"),
        ]

        with ui.row().classes("items-center gap-1"):
            for name, path in pages:
                btn = ui.button(name, on_click=lambda p=path: ui.navigate.to(p))
                if name == active:
                    btn.props("flat color=white").classes("bg-primary text-white")
                else:
                    btn.props("flat").classes("text-grey-4")


ui.run(host="0.0.0.0", port=config.APP_PORT, title="QueryForge v2", reload=False)
