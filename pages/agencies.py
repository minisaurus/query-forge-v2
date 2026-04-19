import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.database import get_session, Agency
from models.qdrant_agents import get_unique_agencies


def render():
    ui.label("Agencies").classes("text-h4 q-mb-md")

    session = get_session()
    try:
        _render_agencies(session)
    finally:
        session.close()


def _render_agencies(session):
    agencies_db = session.query(Agency).all()
    agencies_qdrant = get_unique_agencies()

    all_names = sorted(set(
        [a.name for a in agencies_db] + agencies_qdrant
    ))

    with ui.row().classes("w-full items-end gap-2 q-mb-md"):
        search = ui.input(label="Filter", placeholder="Agency name...").classes("flex-1")
        ui.button("Refresh", icon="refresh", on_click=lambda: ui.navigate.to("/agencies")).classes("q-mb-sm")

    agency_list = ui.column().classes("w-full gap-2")

    def load_agencies():
        agency_list.clear()
        with agency_list:
            for name in all_names:
                if search.value and search.value.lower() not in name.lower():
                    continue

                db_record = next((a for a in agencies_db if a.name == name), None)

                with ui.card().classes("w-full"):
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.label(name).classes("text-h6")
                        with ui.row().classes("gap-1"):
                            if db_record and db_record.guidelines_parsed:
                                ui.badge("Guidelines Parsed", color="green")
                            elif db_record and db_record.guidelines_raw:
                                ui.badge("Guidelines Raw", color="orange")
                            else:
                                ui.badge("No Guidelines", color="grey")

                    if db_record:
                        if db_record.website:
                            ui.link(db_record.website, db_record.website, new_tab=True)
                        if db_record.location:
                            ui.label(f"Location: {db_record.location}").classes("text-caption")
                        if db_record.size:
                            ui.label(f"Size: {db_record.size}").classes("text-caption")
                        if db_record.guidelines_url:
                            ui.link("Submission Guidelines", db_record.guidelines_url, new_tab=True).classes("text-caption")

                    with ui.expansion("Parsed Guidelines" if db_record and db_record.guidelines_parsed else "Details", icon="info").classes("w-full q-mt-sm"):
                        if db_record and db_record.guidelines_parsed:
                            gp = db_record.guidelines_parsed
                            for key, val in gp.items():
                                if val and val not in ([], {}, None, ""):
                                    with ui.row().classes("gap-2"):
                                        ui.label(f"{key.replace('_', ' ').title()}:").classes("text-bold text-body2")
                                        ui.label(str(val)).classes("text-body2")
                        else:
                            ui.label("No parsed guidelines yet. Use the Scraper to fetch them.").classes("text-grey")

    load_agencies()
