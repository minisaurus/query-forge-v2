import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.database import get_session, Manuscript, Author, QueryLetter, Agency
from models.qdrant_agents import get_agent_by_name, get_all_agents, get_unique_agencies
from services.letter_writer import write_query_letter
from services.letter_auditor import audit_letter
from services.mail_merge import assemble_letter
from services.guidelines_parser import get_parsed_guidelines
from services.comp_matcher import get_comp_context


def render():
    ui.label("Query Letter Generator").classes("text-h4 q-mb-md")

    session = get_session()
    try:
        manuscripts = session.query(Manuscript).all()
        agencies_list = get_unique_agencies()

        if not manuscripts:
            ui.label("No manuscripts found. Create one first.").classes("text-grey")
            return

        ms_options = {ms.id: ms.title for ms in manuscripts}
        ms_map = {ms.id: ms for ms in manuscripts}

        with ui.row().classes("w-full items-end gap-2 q-mb-md"):
            ms_select = ui.select(options=ms_options, label="Manuscript", value=manuscripts[0].id if manuscripts else None).classes("flex-1")
            agency_select = ui.select(options=["All"] + agencies_list, label="Agency", value="All").classes("w-60")

        agent_select_container = ui.column().classes("w-full")

        def load_agents():
            agent_select_container.clear()
            with agent_select_container:
                agency_name = agency_select.value
                if agency_name == "All":
                    agents = get_all_agents(limit=500)
                else:
                    agents = get_all_agents(limit=500)
                    agents = [a for a in agents if a.get("agency") == agency_name]

                if not agents:
                    ui.label("No agents found for this filter.").classes("text-grey")
                    return

                agent_options = {f"{a['name']} — {a.get('agency', '?')}" for a in agents}
                agent_options_map = {f"{a['name']} — {a.get('agency', '?')}": a for a in agents}

                agent_select = ui.select(
                    "Select Agent",
                    options=sorted(agent_options),
                ).classes("w-full")

                ui.button("Generate Query Letter", icon="mail", on_click=lambda: _generate(
                    session, ms_map, ms_select.value, agent_select.value, agent_options_map
                )).props("color=primary").classes("q-mt-md")

        agency_select.on_value_change(lambda: load_agents())
        load_agents()

        ui.separator().classes("q-my-lg")

        letter_output = ui.column().classes("w-full")

    finally:
        session.close()


def _generate(session, ms_map, ms_id, agent_key, agent_options_map):
    if not ms_id or not agent_key:
        ui.notify("Select a manuscript and agent first", type="warning")
        return

    ms = ms_map.get(ms_id)
    if not ms:
        ui.notify("Manuscript not found", type="negative")
        return

    agent = agent_options_map.get(agent_key)
    if not agent:
        ui.notify("Agent not found", type="negative")
        return

    try:
        ui.notify("Generating query letter...", type="info")

        guidelines = get_parsed_guidelines(agent.get("agency", ""))

        comp_context = get_comp_context({
            "comp_title_1": ms.comp_title_1,
            "comp_author_1": ms.comp_author_1,
            "comp_title_2": ms.comp_title_2,
            "comp_author_2": ms.comp_author_2,
        })

        manuscript_dict = {
            "title": ms.title,
            "genre": ms.genre,
            "word_count": ms.word_count,
            "hook": ms.hook,
            "synopsis": ms.synopsis,
            "comp_title_1": ms.comp_title_1,
            "comp_author_1": ms.comp_author_1,
            "comp_title_2": ms.comp_title_2,
            "comp_author_2": ms.comp_author_2,
        }

        custom_content = write_query_letter(manuscript_dict, agent, guidelines, comp_context)

        author = ms.author_rel if ms.author_id else None
        full_letter = assemble_letter(manuscript_dict, agent, custom_content, author)

        audit_result = audit_letter(full_letter, manuscript_dict)

        letter = QueryLetter(
            manuscript_id=ms.id,
            agent_name=agent.get("name", ""),
            agency_name=agent.get("agency", ""),
            fixed_content="",
            custom_content=custom_content,
            full_letter=full_letter,
            grade=audit_result.get("grade", ""),
            score=audit_result.get("total", 0),
            critique=audit_result,
            guidelines_used=str(guidelines) if guidelines else None,
        )
        session.add(letter)
        session.commit()

        ui.notify(f"Letter generated! Grade: {audit_result.get('grade', '?')}", type="positive")

    except Exception as e:
        session.rollback()
        ui.notify(f"Error: {e}", type="negative")
