import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from models.database import get_session, Author


def render():
    ui.label("Authors").classes("text-h4 q-mb-md")

    session = get_session()
    try:
        authors = session.query(Author).all()
        _render_list(session, authors)
    finally:
        session.close()


def _render_list(session, authors):
    ui.button("New Author", icon="add", on_click=lambda: _open_form(session)).classes("q-mb-md")

    author_list = ui.column().classes("w-full gap-2")

    with author_list:
        if not authors:
            ui.label("No authors yet. Create one to get started.").classes("text-grey q-pa-md")
            return

        for a in authors:
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(a.name).classes("text-h6")
                    with ui.row().classes("gap-1"):
                        ui.button("Edit", icon="edit", on_click=lambda author=a: _open_form(session, author)).props("flat dense")
                        ui.button("Delete", icon="delete", on_click=lambda author=a: _delete_author(session, author)).props("flat dense color=negative")

                if a.email:
                    ui.label(a.email).classes("text-body2 text-grey")
                if a.bio:
                    ui.label(a.bio[:200]).classes("text-body2 q-mt-xs")

                socials = a.social_links or {}
                with ui.row().classes("gap-2 q-mt-xs"):
                    for platform in ["twitter", "instagram", "facebook", "tiktok"]:
                        handle = socials.get(platform)
                        if handle:
                            ui.chip(f"{platform}: {handle}", size="sm", removable=False).props("outline dense")


def _open_form(session, author=None):
    dialog = ui.dialog().classes("w-full max-w-2xl")
    with dialog:
        with ui.card().classes("w-full"):
            ui.label("Edit Author" if author else "New Author").classes("text-h6 q-mb-md")

            name = ui.input(label="Name *", value=author.name if author else "").classes("w-full")
            email = ui.input(label="Email", value=author.email if author else "").classes("w-full")
            phone = ui.input(label="Phone", value=author.phone if author else "").classes("w-full")
            website = ui.input(label="Website", value=author.website if author else "").classes("w-full")

            socials = author.social_links if author else {}
            with ui.row().classes("w-full gap-2"):
                twitter = ui.input(label="Twitter/X", value=socials.get("twitter", "")).classes("flex-1")
                instagram = ui.input(label="Instagram", value=socials.get("instagram", "")).classes("flex-1")
            with ui.row().classes("w-full gap-2"):
                facebook = ui.input(label="Facebook", value=socials.get("facebook", "")).classes("flex-1")
                tiktok = ui.input(label="TikTok", value=socials.get("tiktok", "")).classes("flex-1")

            bio = ui.textarea("Author Bio", value=author.bio if author else "").classes("w-full").props("rows=4")
            background = ui.textarea("Personal Background", value=author.personal_background if author else "").classes("w-full").props("rows=3")

            with ui.row().classes("q-mt-md gap-2"):
                ui.button("Save", on_click=lambda: _save(
                    session, dialog, author,
                    name.value, email.value, phone.value, website.value,
                    twitter.value, instagram.value, facebook.value, tiktok.value,
                    bio.value, background.value,
                )).props("color=primary")
                ui.button("Cancel", on_click=dialog.close).props("flat")

    dialog.open()


def _save(session, dialog, existing, name, email, phone, website, twitter, instagram, facebook, tiktok, bio, background):
    if not name:
        ui.notify("Name is required", type="warning")
        return

    social_links = {}
    if twitter:
        social_links["twitter"] = twitter
    if instagram:
        social_links["instagram"] = instagram
    if facebook:
        social_links["facebook"] = facebook
    if tiktok:
        social_links["tiktok"] = tiktok

    try:
        if existing:
            author = session.query(Author).get(existing.id)
        else:
            author = Author()
            session.add(author)

        author.name = name
        author.email = email or None
        author.phone = phone or None
        author.website = website or None
        author.social_links = social_links if social_links else None
        author.bio = bio or None
        author.personal_background = background or None

        session.commit()
        dialog.close()
        ui.notify("Author saved", type="positive")
        ui.navigate.to("/authors")
    except Exception as e:
        session.rollback()
        ui.notify(f"Error: {e}", type="negative")


def _delete_author(session, author):
    session.delete(author)
    session.commit()
    ui.notify("Author deleted", type="info")
    ui.navigate.to("/authors")
