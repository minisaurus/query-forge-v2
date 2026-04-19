import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.qdrant_books import search_books, get_books_by_genre


def find_comps(manuscript: dict, limit: int = 10) -> list[dict]:
    genre = manuscript.get("genre", "")
    hook = manuscript.get("hook", "")
    synopsis = manuscript.get("synopsis", "")

    query = f"{genre} {hook} {synopsis[:200]}".strip()

    return search_books(query, limit=limit)


def get_comp_context(manuscript: dict) -> str:
    comp_1 = manuscript.get("comp_title_1", "")
    comp_author_1 = manuscript.get("comp_author_1", "")
    comp_2 = manuscript.get("comp_title_2", "")
    comp_author_2 = manuscript.get("comp_author_2", "")

    if not comp_1:
        return ""

    parts = ["Comparable titles provided by author:"]
    if comp_1:
        info_1 = _lookup_comp(comp_1, comp_author_1)
        parts.append(f"- {comp_1} by {comp_author_1}{info_1}")
    if comp_2:
        info_2 = _lookup_comp(comp_2, comp_author_2)
        parts.append(f"- {comp_2} by {comp_author_2}{info_2}")

    return "\n".join(parts)


def _lookup_comp(title: str, author: str) -> str:
    try:
        results = search_books(f"{title} by {author}", limit=1)
        if results:
            r = results[0]
            rating = r.get("goodreads_rating", 0)
            ratings_count = r.get("goodreads_ratings_count", 0)
            if rating:
                return f" (Goodreads: {float(rating):.2f}, {int(float(ratings_count)):,} ratings)"
    except Exception:
        pass
    return ""


def suggest_comps(genre: str, description: str = "", limit: int = 5) -> list[dict]:
    genre_books = get_books_by_genre(genre)

    if not genre_books:
        if description:
            return search_books(f"{genre} {description}", limit=limit)
        return search_books(genre, limit=limit)

    rated = []
    for b in genre_books:
        try:
            r = float(b.get("goodreads_rating", 0))
        except (ValueError, TypeError):
            r = 0
        rated.append((r, b))

    rated.sort(key=lambda x: x[0], reverse=True)

    return [b for _, b in rated[:limit]]
