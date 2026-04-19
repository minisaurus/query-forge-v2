import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.qdrant_agents import get_unique_genres


def render():
    ui.label("Agent Scraper").classes("text-h4 q-mb-md")

    genres = get_unique_genres()

    with ui.card().classes("w-full"):
        ui.label("Scrape Agent Directories").classes("text-h6")
        ui.label("Search agent directories (QueryTracker, AgentQuery, MSWishList, AAR) for literary agents by genre.").classes("text-body2 text-grey q-mb-md")

        genre_input = ui.input(label="Genre", value="", placeholder="e.g., fantasy, literary fiction...").classes("w-full")
        with ui.row().classes("gap-2"):
            ui.select(options=genres, label="Quick Add", value=None).classes("w-60")

        ui.number(label="Books per source", value=25, min=5, max=100).classes("w-40")
        ui.button("Start Scraping", icon="cloud_download", on_click=lambda: _scrape()).props("color=primary").classes("q-mt-md")

        output = ui.textarea(label="Output", value="").classes("w-full q-mt-md").props("rows=10 readonly")

    ui.separator().classes("q-my-lg")

    with ui.card().classes("w-full"):
        ui.label("Sync Agency Guidelines").classes("text-h6")
        ui.label("Scrape submission guidelines for all agencies in the database.").classes("text-body2 text-grey q-mb-md")

        ui.button("Sync All Guidelines", icon="sync", on_click=lambda: _sync_guidelines()).props("color=secondary")
        guidelines_output = ui.textarea(label="Output", value="").classes("w-full q-mt-md").props("rows=10 readonly")

    ui.separator().classes("q-my-lg")

    with ui.card().classes("w-full"):
        ui.label("Enrich Agent Data").classes("text-h6")
        ui.label("Fill in missing agent data (email, website, location) by searching the web.").classes("text-body2 text-grey q-mb-md")

        ui.button("Enrich All Agents", icon="auto_fix_high", on_click=lambda: _enrich()).props("color=secondary")
        enrich_output = ui.textarea(label="Output", value="").classes("w-full q-mt-md").props("rows=10 readonly")


def _scrape():
    ui.notify("Scraper not yet connected — coming soon", type="info")


def _sync_guidelines():
    ui.notify("Guidelines sync not yet connected — coming soon", type="info")


def _enrich():
    ui.notify("Enrichment not yet connected — coming soon", type="info")
