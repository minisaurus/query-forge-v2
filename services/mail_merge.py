import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def assemble_letter(
    manuscript: dict,
    agent: dict,
    custom_content: str,
    author: dict | None = None,
) -> str:
    author = author or manuscript.get("author_rel") or {}

    author_name = author.get("name", "[Author Name]")
    author_email = author.get("email", "[email]")
    author_phone = author.get("phone", "")
    author_website = author.get("website", "")
    author_bio = author.get("bio", "")

    agent_name = agent.get("name", "[Agent Name]")
    agency = agent.get("agency", "[Agency]")
    agency_website = agent.get("agency_website", "")

    title = manuscript.get("title", "[Title]")
    genre = manuscript.get("genre", "")
    word_count = manuscript.get("word_count", "")

    comp_1 = manuscript.get("comp_title_1", "")
    comp_author_1 = manuscript.get("comp_author_1", "")
    comp_2 = manuscript.get("comp_title_2", "")
    comp_author_2 = manuscript.get("comp_author_2", "")

    parts = []

    header = f"{author_name}"
    if author_email:
        header += f"\n{author_email}"
    if author_phone:
        header += f"\n{author_phone}"
    if author_website:
        header += f"\n{author_website}"
    parts.append(header)

    parts.append("")
    parts.append("[Date]")
    parts.append("")

    agency_block = agent_name
    if agency:
        agency_block += f"\n{agency}"
    parts.append(agency_block)
    parts.append("")

    parts.append(f"Re: Query for {title}")
    parts.append("")

    parts.append(f"Dear {agent_name.split()[0] if agent_name else 'Agent'},")
    parts.append("")

    parts.append(custom_content)

    if word_count or genre:
        parts.append("")
        detail_parts = []
        if genre:
            detail_parts.append(genre)
        if word_count:
            detail_parts.append(f"{word_count:,} words")
        parts.append(f"{'complete at ' if word_count else ''}{', '.join(detail_parts)}. Full manuscript available upon request.")

    if author_bio:
        parts.append("")
        parts.append(author_bio)

    parts.append("")
    parts.append(f"Thank you for your time and consideration.")
    parts.append("")
    parts.append(f"Sincerely,")
    parts.append(f"{author_name}")

    return "\n".join(parts)


def letter_to_plain_text(letter: str) -> str:
    return letter


def letter_to_html(letter: str) -> str:
    paragraphs = letter.split("\n\n")
    html_parts = []
    for p in paragraphs:
        lines = p.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Re:"):
                html_parts.append(f"<h3>{line}</h3>")
            elif line in ("Sincerely,", "[Date]"):
                html_parts.append(f"<p><em>{line}</em></p>")
            else:
                html_parts.append(f"<p>{line}</p>")
    return "\n".join(html_parts)
