import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.qdrant_agents import get_agent_count, get_unique_agencies, get_unique_genres
from models.qdrant_books import get_book_count, get_genres as get_book_genres
from models.database import get_session, Manuscript, Author, QueryLetter


def render():
    session = get_session()
    try:
        agent_count = get_agent_count()
        agency_count = len(get_unique_agencies())
        book_count = get_book_count()
        book_genres = get_book_genres()
        manuscript_count = session.query(Manuscript).count()
        author_count = session.query(Author).count()
        letter_count = session.query(QueryLetter).count()
    except Exception:
        agent_count = 0
        agency_count = 0
        book_count = 0
        book_genres = []
        manuscript_count = 0
        author_count = 0
        letter_count = 0
    finally:
        session.close()

    ui.label("Dashboard").classes("text-h4 q-mb-md")

    with ui.row().classes("w-full gap-4"):
        _stat_card("Agents", agent_count, "in Qdrant")
        _stat_card("Agencies", agency_count, "unique")
        _stat_card("Books", book_count, "in qdrant-forge")
        _stat_card("Book Genres", len(book_genres), "genres")
        _stat_card("Manuscripts", manuscript_count, "saved")
        _stat_card("Authors", author_count, "profiles")
        _stat_card("Query Letters", letter_count, "generated")

    ui.label("Quick Actions").classes("text-h6 q-mt-lg q-mb-sm")

    with ui.row().classes("gap-3"):
        ui.button("Find Agents", icon="search", on_click=lambda: ui.navigate.to("/agents")).props("outline")
        ui.button("New Manuscript", icon="add", on_click=lambda: ui.navigate.to("/manuscripts")).props("outline")
        ui.button("Generate Letter", icon="mail", on_click=lambda: ui.navigate.to("/query-letters")).props("outline")
        ui.button("Run Scraper", icon="cloud_download", on_click=lambda: ui.navigate.to("/scraper")).props("outline")


def _stat_card(title: str, value, subtitle: str):
    with ui.card().classes("w-40 text-center"):
        ui.label(str(value)).classes("text-h4 font-bold")
        ui.label(title).classes("text-subtitle2")
        ui.label(subtitle).classes("text-caption text-grey")
