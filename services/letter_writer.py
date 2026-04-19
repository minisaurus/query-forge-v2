import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_client import call_llm


def write_query_letter(
    manuscript: dict,
    agent: dict,
    guidelines: dict | None,
    comp_context: str = "",
) -> str:
    author = manuscript.get("author_rel") or {}
    author_name = author.get("name", "[Author Name]")
    author_bio = author.get("bio", "")

    title = manuscript.get("title", "")
    genre = manuscript.get("genre", "")
    hook = manuscript.get("hook", "")
    synopsis = manuscript.get("synopsis", "")
    comp_1 = manuscript.get("comp_title_1", "")
    comp_author_1 = manuscript.get("comp_author_1", "")
    comp_2 = manuscript.get("comp_title_2", "")
    comp_author_2 = manuscript.get("comp_author_2", "")
    word_count = manuscript.get("word_count", "")

    agent_name = agent.get("name", "")
    agent_bio = agent.get("bio", "")
    agent_genres = ", ".join(agent.get("genres", []))
    agency = agent.get("agency", "")

    guidelines_text = ""
    if guidelines:
        guidelines_text = f"""Agency Submission Guidelines:
- Required materials: {guidelines.get('materials_required', ['query letter'])}
- Submission method: {guidelines.get('submission_method', 'unknown')}
- Special instructions: {guidelines.get('special_instructions', 'none')}
- Excluded: {guidelines.get('excluded', 'none')}"""

    system = """You are an expert query letter writer for literary fiction. Write ONLY the personalized body paragraphs of a query letter — do NOT include the header, date, addresses, salutation, author bio, or closing.

The letter body should be 200-300 words and include:
1. A personalization line showing why this agent is a good fit (reference their interests/clients)
2. The hook — a compelling one-sentence pitch
3. A brief synopsis of the story (protagonist, stakes, conflict — no ending)
4. Comp titles if provided (one line: "X meets Y" or "for fans of X and Y")
5. Practical details (word count, genre, availability of full manuscript)

Write in a confident, professional voice. Be specific and vivid."""

    user = f"""Write the personalized query letter body for:

AUTHOR: {author_name}
TITLE: {title}
GENRE: {genre}
WORD COUNT: {word_count}
HOOK: {hook}

SYNOPSIS:
{synopsis}

COMP TITLES: {comp_1} by {comp_author_1}{' / ' + comp_2 + ' by ' + comp_author_2 if comp_2 else '' if comp_1 else 'None provided'}
{comp_context}

TARGET AGENT: {agent_name} at {agency}
AGENT BIO: {agent_bio}
AGENT GENRES: {agent_genres}

{guidelines_text}

Write the query letter body paragraphs now."""

    return call_llm(system, user, temperature=0.7, max_tokens=1000)
