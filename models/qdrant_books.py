import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import config


def get_client() -> QdrantClient:
    return QdrantClient(
        host=config.QDRANT_HOST,
        port=config.QDRANT_PORT,
        check_compatibility=False,
    )


def get_genres() -> list[str]:
    books = get_all_books(limit=2000)
    genres = set()
    for b in books:
        g = b.get("genre", "")
        if g:
            genres.add(g)
    return sorted(genres)


def get_all_books(genre: str = None, limit: int = 500) -> list[dict]:
    client = get_client()

    scroll_filter = None
    if genre:
        scroll_filter = Filter(must=[FieldCondition(key="genre", match=MatchValue(value=genre))])

    all_books = []
    offset = None
    while True:
        results, offset = client.scroll(
            collection_name=config.QDRANT_BOOKS_COLLECTION,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
            scroll_filter=scroll_filter,
        )
        for p in results:
            all_books.append(p.payload)
        if offset is None:
            break
        if len(all_books) >= limit:
            break

    return all_books[:limit]


def search_books(query: str, limit: int = 10) -> list[dict]:
    from llm_client import get_embedding
    client = get_client()
    vector = get_embedding(query)

    results = client.query_points(
        collection_name=config.QDRANT_BOOKS_COLLECTION,
        query=vector,
        limit=limit,
        with_payload=True,
    )

    return [{**r.payload, "_score": r.score} for r in results.points]


def get_book_count() -> int:
    client = get_client()
    info = client.get_collection(config.QDRANT_BOOKS_COLLECTION)
    return info.points_count


def get_books_by_genre(genre: str) -> list[dict]:
    return get_all_books(genre=genre, limit=500)


def find_comp_titles(genre: str, description: str = "", limit: int = 10) -> list[dict]:
    query = f"{genre} {description}".strip()
    results = search_books(query, limit=limit)

    for b in results:
        rating = b.get("goodreads_rating", 0)
        try:
            b["rating_display"] = f"{float(rating):.2f}" if rating else "—"
        except (ValueError, TypeError):
            b["rating_display"] = "—"

    return results
