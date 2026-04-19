import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.database import get_session, Manuscript, Author
from services.comp_matcher import suggest_comps


def render():
    ui.label("Manuscripts").classes("text-h4 q-mb-md")

    session = get_session()
    try:
        authors = session.query(Author).all()
        author_options = {a.id: a.name for a in authors}
        manuscripts = session.query(Manuscript).all()

        ui.button("New Manuscript", icon="add", on_click=lambda: _open_form(session, author_options)).classes("q-mb-md")

        ms_list = ui.column().classes("w-full gap-2")

        def refresh():
            ms_list.clear()
            all_ms = session.query(Manuscript).all()
            with ms_list:
                if not all_ms:
                    ui.label("No manuscripts yet. Create one to get started.").classes("text-grey q-pa-md")
                    return

                for ms in all_ms:
                    with ui.card().classes("w-full"):
                        with ui.row().classes("items-center justify-between w-full"):
                            ui.label(ms.title).classes("text-h6")
                            with ui.row().classes("gap-1"):
                                if ms.genre:
                                    ui.badge(ms.genre, color="primary").props("outline")
                                if ms.word_count:
                                    ui.badge(f"{ms.word_count:,} words", color="grey").props("outline")

                        if ms.hook:
                            ui.label(ms.hook).classes("text-body2 text-grey q-mt-xs")

                        with ui.row().classes("q-mt-sm gap-1"):
                            ui.button("Edit", icon="edit", on_click=lambda m=ms: _open_form(session, author_options, m)).props("flat dense")
                            ui.button("Delete", icon="delete", on_click=lambda m=ms: _delete_ms(session, m)).props("flat dense color=negative")

                            if ms.genre:
                                ui.button("Suggest Comps", icon="search", on_click=lambda m=ms: _show_comps(m)).props("flat dense")

        refresh()

    finally:
        session.close()


def _show_comps(ms):
    try:
        results = suggest_comps(ms.genre or "", ms.hook or "")

        dialog = ui.dialog().classes("w-full max-w-3xl")
        with dialog:
            with ui.card().classes("w-full"):
                ui.label("Suggested Comp Titles").classes("text-h6")
                if not results:
                    ui.label("No comp suggestions found in qdrant-forge.").classes("text-grey q-pa-md")
                else:
                    for b in results:
                        with ui.row().classes("items-center gap-4 w-full"):
                            ui.label(b.get("title", "?")).classes("font-bold")
                            ui.label(f"by {b.get('author', '?')}").classes("text-grey")
                            try:
                                r = float(b.get("goodreads_rating", 0))
                                if r:
                                    ui.label(f"\u2605 {r:.2f}").classes("text-amber")
                            except (ValueError, TypeError):
                                pass
                            if b.get("published_year"):
                                ui.label(str(b["published_year"])).classes("text-grey")
                ui.button("Close", on_click=dialog.close).props("flat")
        dialog.open()
    except Exception as e:
        ui.notify(f"Error: {e}", type="negative")


def _open_form(session, author_options, ms=None):
    dialog = ui.dialog().classes("w-full max-w-2xl")
    with dialog:
        with ui.card().classes("w-full"):
            ui.label("Edit Manuscript" if ms else "New Manuscript").classes("text-h6 q-mb-md")

            title = ui.input(label="Title *", value=ms.title if ms else "").classes("w-full")
            genre = ui.input(label="Genre", value=ms.genre if ms else "").classes("w-full")
            word_count = ui.number(label="Word Count", value=float(ms.word_count) if ms and ms.word_count else None).classes("w-full")
            hook = ui.textarea(label="Hook (1-2 sentence pitch)", value=ms.hook if ms else "").classes("w-full")
            synopsis = ui.textarea(label="Synopsis", value=ms.synopsis if ms else "").classes("w-full").props("rows=6")

            with ui.row().classes("w-full gap-2"):
                comp_title_1 = ui.input(label="Comp Title 1", value=ms.comp_title_1 if ms else "").classes("flex-1")
                comp_author_1 = ui.input(label="Comp Author 1", value=ms.comp_author_1 if ms else "").classes("flex-1")

            with ui.row().classes("w-full gap-2"):
                comp_title_2 = ui.input(label="Comp Title 2", value=ms.comp_title_2 if ms else "").classes("flex-1")
                comp_author_2 = ui.input(label="Comp Author 2", value=ms.comp_author_2 if ms else "").classes("flex-1")

            author_id = ui.select(options=author_options, label="Author", value=ms.author_id if ms else None).classes("w-full")
            notes = ui.textarea(label="Notes", value=ms.notes if ms else "").classes("w-full")

            with ui.row().classes("q-mt-md gap-2"):
                ui.button("Save", on_click=lambda: _save(
                    session, dialog, ms,
                    title.value, genre.value, word_count.value,
                    hook.value, synopsis.value,
                    comp_title_1.value, comp_author_1.value,
                    comp_title_2.value, comp_author_2.value,
                    author_id.value, notes.value,
                )).props("color=primary")
                ui.button("Cancel", on_click=dialog.close).props("flat")

    dialog.open()


def _save(session, dialog, existing, title, genre, word_count, hook, synopsis,
          comp_title_1, comp_author_1, comp_title_2, comp_author_2, author_id, notes):
    if not title:
        ui.notify("Title is required", type="warning")
        return

    try:
        if existing:
            ms = session.query(Manuscript).get(existing.id)
        else:
            ms = Manuscript()
            session.add(ms)

        ms.title = title
        ms.genre = genre or None
        ms.word_count = int(word_count) if word_count else None
        ms.hook = hook or None
        ms.synopsis = synopsis or None
        ms.comp_title_1 = comp_title_1 or None
        ms.comp_author_1 = comp_author_1 or None
        ms.comp_title_2 = comp_title_2 or None
        ms.comp_author_2 = comp_author_2 or None
        ms.author_id = author_id
        ms.notes = notes or None

        session.commit()
        dialog.close()
        ui.notify("Manuscript saved", type="positive")
        ui.navigate.to("/manuscripts")
    except Exception as e:
        session.rollback()
        ui.notify(f"Error: {e}", type="negative")


def _delete_ms(session, ms):
    try:
        session.delete(ms)
        session.commit()
        ui.notify("Manuscript deleted", type="info")
        ui.navigate.to("/manuscripts")
    except Exception as e:
        session.rollback()
        ui.notify(f"Error: {e}", type="negative")
