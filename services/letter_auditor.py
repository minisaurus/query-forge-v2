import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_client import call_llm_json


def audit_letter(full_letter: str, manuscript: dict) -> dict:
    title = manuscript.get("title", "")
    genre = manuscript.get("genre", "")
    hook = manuscript.get("hook", "")
    synopsis = manuscript.get("synopsis", "")

    system = """You are a query letter auditor for literary fiction. Grade the query letter on these 8 criteria, each scored 0-2.5:

1. PERSONALIZATION — Does it show why this specific agent is a fit?
2. HOOK — Is the opening compelling and concise (under 40 words)?
3. COMP TITLES — Are comps appropriate and well-integrated?
4. SYNOPSIS CLARITY — Is the story clear (protagonist, conflict, stakes)?
5. SYNOPSIS STAKES — Do we care what happens?
6. VOICE — Is the writing confident and professional?
7. LENGTH — Is it 200-300 words?
8. PROFESSIONALISM — Correct tone, no red flags?

Return JSON:
{
  "scores": {"personalization": X, "hook": X, "comp_titles": X, "synopsis_clarity": X, "synopsis_stakes": X, "voice": X, "length": X, "professionalism": X},
  "total": X,
  "grade": "A+/A/A-/B+/B/C/D/F",
  "key_fixes": ["list of the 3 most important improvements"],
  "strengths": ["what works well"],
  "line_by_line": ["specific line-level feedback"]
}

Grade scale: A+ (20-19), A (18-17), A- (16-15), B+ (14-12), B (11-9), C (8-6), D/F (5-0)"""

    user = f"""Manuscript: {title} ({genre})
Original hook: {hook}
Synopsis: {synopsis[:500]}

QUERY LETTER TO AUDIT:
{full_letter}

Grade this query letter."""

    return call_llm_json(system, user, temperature=0.3)
