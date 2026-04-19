import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.qdrant_agents import search_agents, get_all_agents, get_unique_genres, get_agent_count


def render():
    ui.label("Agent Database").classes("text-h4 q-mb-md")

    genres = ["All"] + get_unique_genres()

    with ui.row().classes("w-full items-end gap-2 q-mb-md"):
        search_input = ui.input(label="Search", placeholder="Natural language query...").classes("flex-1")
        genre_select = ui.select(options=genres, label="Genre", value="All").classes("w-60")
        accepts_new = ui.checkbox("Accepting new only", value=False)
        ui.button("Search", icon="search", on_click=lambda: do_search()).classes("q-mb-sm")

    count_label = ui.label()
    agent_list = ui.column().classes("w-full gap-2")

    def do_search():
        query_text = search_input.value or ""
        genre = genre_select.value if genre_select.value != "All" else None
        new_only = accepts_new.value

        try:
            if query_text:
                results = search_agents(query_text, genre=genre, accepts_new=new_only, limit=50)
            else:
                results = get_all_agents(genre=genre, limit=200)
                if new_only:
                    results = [a for a in results if a.get("accepts_new_authors") == "Yes"]

            total = get_agent_count()
            count_label.text = f"Showing {len(results)} of {total} agents"

            agent_list.clear()
            with agent_list:
                if not results:
                    ui.label("No agents found. Try a different search.").classes("text-grey q-pa-md")
                    return

                for a in results:
                    _render_agent_card(a)
        except Exception as e:
            ui.notify(f"Error: {e}", type="negative")

    do_search()


def _render_agent_card(a: dict):
    with ui.card().classes("w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(a.get("name", "Unknown")).classes("text-h6")
            with ui.row().classes("gap-1"):
                if a.get("accepts_new_authors") == "Yes":
                    ui.badge("Accepting", color="green")
                elif a.get("accepts_new_authors") == "No":
                    ui.badge("Closed", color="red")
                if a.get("agency_size"):
                    ui.badge(a["agency_size"], color="grey")

        ui.label(a.get("agency", "")).classes("text-subtitle2 text-grey")

        if a.get("genres"):
            with ui.row().classes("gap-1 q-mt-xs"):
                for g in a["genres"][:5]:
                    ui.chip(g, size="sm").props("outline dense")
                if len(a["genres"]) > 5:
                    ui.chip(f"+{len(a['genres']) - 5} more", size="sm").props("outline dense")

        with ui.row().classes("q-mt-sm gap-1"):
            if a.get("email") and a["email"] not in ("", "Not found"):
                ui.badge(f"Email: {a['email']}", color="blue").props("outline")
            if a.get("submission_method") and a["submission_method"] != "Unknown":
                ui.badge(a["submission_method"], color="purple").props("outline")
            if a.get("response_time") and a["response_time"] != "Unknown":
                ui.badge(f"Response: {a['response_time']}", color="teal").props("outline")

        with ui.expansion("Details", icon="info").classes("w-full q-mt-sm"):
            _render_agent_details(a)

        if a.get("submission_guidelines_url"):
            ui.link("View Submission Guidelines", a["submission_guidelines_url"], new_tab=True).classes("q-mt-sm")


def _render_agent_details(a: dict):
    with ui.row().classes("w-full gap-8"):
        with ui.column().classes("flex-1"):
            if a.get("bio"):
                ui.label("Bio").classes("text-bold")
                ui.label(a["bio"]).classes("text-body2")

            if a.get("notes"):
                ui.label("Notes").classes("text-bold q-mt-sm")
                ui.label(a["notes"]).classes("text-body2")

        with ui.column().classes("flex-1"):
            fields = [
                ("Location", a.get("location")),
                ("Phone", a.get("phone")),
                ("Website", a.get("website") or a.get("agency_website")),
                ("Preferred Contact", a.get("preferred_contact")),
                ("Source", a.get("source")),
            ]
            for label, value in fields:
                if value and value not in ("", "Unknown", "Not found"):
                    with ui.row().classes("gap-2"):
                        ui.label(f"{label}:").classes("text-bold text-body2")
                        ui.label(value).classes("text-body2")
