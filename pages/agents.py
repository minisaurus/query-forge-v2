import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.qdrant_agents import search_agents, get_all_agents, get_unique_genres, get_agent_count

PAGE_SIZE = 20


def render():
    ui.label("Agent Database").classes("text-h4 q-mb-md")

    genres = ["All"] + get_unique_genres()
    all_agents = get_all_agents(limit=2000)
    current_page = [0]

    with ui.row().classes("w-full items-end gap-2 q-mb-md"):
        search_input = ui.input(label="Search", placeholder="Natural language query...").classes("flex-1")
        genre_select = ui.select(options=genres, label="Genre", value="All").classes("w-60")
        accepts_new = ui.checkbox("Accepting new only", value=False)
        ui.button("Search", icon="search", on_click=lambda: do_search()).classes("q-mb-sm")

    count_label = ui.label()
    agent_list = ui.column().classes("w-full gap-2")
    pagination_row = ui.row().classes("w-full justify-center q-mt-md")

    def do_search():
        query_text = search_input.value.strip()
        genre = genre_select.value if genre_select.value != "All" else None
        new_only = accepts_new.value

        if query_text:
            results = search_agents(query_text, genre=genre, accepts_new=new_only, limit=100)
        else:
            results = all_agents
            if genre:
                results = [a for a in results if genre in a.get("genres", [])]
            if new_only:
                results = [a for a in results if a.get("accepts_new_authors") == "Yes"]

        current_page[0] = 0
        total = get_agent_count()
        render_page(results, total)

    def render_page(results, total):
        count_label.text = f"Showing {len(results)} of {total} agents"

        page = current_page[0]
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_agents = results[start:end]

        agent_list.clear()
        with agent_list:
            if not page_agents:
                ui.label("No agents found. Try a different search.").classes("text-grey q-pa-md")
            else:
                for a in page_agents:
                    _render_agent_card(a)

        total_pages = max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)
        pagination_row.clear()
        with pagination_row:
            ui.button("Previous", on_click=lambda: prev_page(results, total), icon="navigate_before").props(
                f"flat dense {"disabled" if page == 0 else ""}"
            )
            ui.label(f"Page {page + 1} of {total_pages}").classes("self-center q-mx-md")
            ui.button("Next", on_click=lambda: next_page(results, total), icon="navigate_next").props(
                f"flat dense {"disabled" if page >= total_pages - 1 else ""}"
            )

    def next_page(results, total):
        current_page[0] += 1
        render_page(results, total)

    def prev_page(results, total):
        current_page[0] = max(0, current_page[0] - 1)
        render_page(results, total)

    do_search()


def _render_agent_card(a: dict):
    with ui.card().classes("w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(a.get("name") or "Unknown").classes("text-h6")
            with ui.row().classes("gap-1"):
                status = a.get("accepts_new_authors", "")
                if status == "Yes":
                    ui.badge("Accepting", color="green")
                elif status == "No":
                    ui.badge("Closed", color="red")
                sz = a.get("agency_size", "")
                if sz and sz != "Unknown":
                    ui.badge(sz, color="grey")

        agency = a.get("agency") or ""
        if agency:
            ui.label(agency).classes("text-subtitle2 text-grey")

        genres = a.get("genres") or []
        if genres:
            with ui.row().classes("gap-1 q-mt-xs"):
                for g in genres[:5]:
                    ui.chip(g).props("outline dense size=sm")
                if len(genres) > 5:
                    ui.chip(f"+{len(genres) - 5} more").props("outline dense size=sm")

        badges = []
        email = a.get("email") or ""
        if email and email not in ("Not found", ""):
            badges.append(("email", email, "blue"))
        method = a.get("submission_method") or ""
        if method and method != "Unknown":
            badges.append(("method", method, "purple"))
        resp = a.get("response_time") or ""
        if resp and resp != "Unknown":
            badges.append(("resp", f"Response: {resp}", "teal"))

        if badges:
            with ui.row().classes("q-mt-sm gap-1"):
                for btype, text, color in badges:
                    ui.badge(text, color=color).props("outline")
                    if btype == "email":
                        def copy_email(e=email):
                            safe = e.replace("'", "\\'")
                            ui.run_javascript(f"navigator.clipboard.writeText('{safe}')")
                            ui.notify(f"Copied: {e}", type="positive", timeout=2)
                        ui.button(icon="content_copy", on_click=copy_email).props("flat dense padding-none color=blue").classes("q-ml-xs").tooltip("Copy email")

        details = []
        if a.get("bio"):
            details.append(("Bio", a["bio"]))
        if a.get("notes"):
            details.append(("Notes", a["notes"]))

        extra = []
        for label, key in [("Location", "location"), ("Phone", "phone"), ("Website", "website"), ("Agency Website", "agency_website"), ("Preferred Contact", "preferred_contact"), ("Source", "source")]:
            val = a.get(key) or ""
            if val and val not in ("Unknown", "Not found", ""):
                extra.append((label, val))

        if details or extra:
            with ui.expansion("Details", icon="info").classes("w-full q-mt-sm"):
                with ui.row().classes("w-full gap-8"):
                    if details:
                        with ui.column().classes("flex-1"):
                            for label, val in details:
                                ui.label(label).classes("text-bold")
                                ui.label(val).classes("text-body2")
                    if extra:
                        with ui.column().classes("flex-1"):
                            for label, val in extra:
                                with ui.row().classes("gap-2"):
                                    ui.label(f"{label}:").classes("text-bold text-body2")
                                    ui.label(val).classes("text-body2")

        guide_url = a.get("submission_guidelines_url") or a.get("guidelines_url") or ""
        if guide_url:
            ui.link("View Submission Guidelines", guide_url, new_tab=True).classes("q-mt-sm")
