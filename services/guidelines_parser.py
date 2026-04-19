import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models.database import get_session, Agency


def get_parsed_guidelines(agency_name: str) -> dict | None:
    session = get_session()
    try:
        agency = session.query(Agency).filter(Agency.name == agency_name).first()
        if agency and agency.guidelines_parsed:
            return agency.guidelines_parsed
        return None
    finally:
        session.close()


def parse_guidelines(agency_name: str, raw_text: str) -> dict:
    from services.llm_client import call_llm_json

    system = """You are a literary publishing expert. Parse submission guidelines into structured JSON.

Return a JSON object with these fields:
{
  "materials_required": ["query letter", "synopsis", "sample pages", etc.],
  "materials_optional": ["author bio", "marketing plan", etc.],
  "word_count_limits": {"min": null, "max": null, "note": "any specific guidance"},
  "submission_method": "email|querymanager|form|other",
  "email_address": null or the email,
  "response_time": "estimated response time or null",
  "simultaneous_submissions": "yes|no|unknown",
  "special_instructions": "any unique requirements or formatting",
  "genres_accepted": ["list of genres mentioned"],
  "excluded": ["anything they explicitly say NOT to send"]
}

Only include fields you can determine from the text. Use null for unknown fields."""

    user = f"""Agency: {agency_name}

Raw guidelines text:
{raw_text[:5000]}

Parse these submission guidelines into structured JSON."""

    try:
        return call_llm_json(system, user, temperature=0.2)
    except Exception as e:
        return {"error": str(e), "raw_length": len(raw_text)}


def save_parsed_guidelines(agency_name: str, guidelines_raw: str, guidelines_parsed: dict, guidelines_url: str = None, website: str = None, location: str = None, size: str = None):
    session = get_session()
    try:
        agency = session.query(Agency).filter(Agency.name == agency_name).first()
        if not agency:
            agency = Agency(name=agency_name)
            session.add(agency)

        if guidelines_url:
            agency.guidelines_url = guidelines_url
        if website:
            agency.website = website
        if location:
            agency.location = location
        if size:
            agency.size = size

        agency.guidelines_raw = guidelines_raw
        agency.guidelines_parsed = guidelines_parsed

        from datetime import datetime
        agency.last_scraped_at = datetime.now()

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
