import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from config import config


def get_client() -> QdrantClient:
    return QdrantClient(
        host=config.QDRANT_HOST,
        port=config.QDRANT_PORT,
        check_compatibility=False,
    )


def agent_id(name: str, agency: str) -> str:
    return hashlib.md5(f"{name.lower()}@{agency.lower()}".encode()).hexdigest()


def search_agents(query: str, limit: int = 20, genre: str = None, accepts_new: bool = False, agency_size: str = None) -> list[dict]:
    from llm_client import get_embedding
    client = get_client()
    vector = get_embedding(query)

    must = []
    if genre:
        must.append(FieldCondition(key="genres", match=MatchValue(any=[genre])))
    if accepts_new:
        must.append(FieldCondition(key="accepts_new_authors", match=MatchValue(value="Yes")))
    if agency_size:
        must.append(FieldCondition(key="agency_size", match=MatchValue(value=agency_size)))

    search_filter = Filter(must=must) if must else None

    results = client.query_points(
        collection_name=config.QDRANT_AGENTS_COLLECTION,
        query=vector,
        limit=limit,
        query_filter=search_filter,
        with_payload=True,
    )

    agents = []
    for r in results.points:
        agents.append({**r.payload, "_score": r.score, "_id": r.id})

    return agents


def get_all_agents(genre: str = None, limit: int = 500) -> list[dict]:
    client = get_client()

    scroll_filter = None
    if genre:
        scroll_filter = Filter(must=[FieldCondition(key="genres", match=MatchValue(any=[genre]))])

    all_agents = []
    offset = None
    while True:
        results, offset = client.scroll(
            collection_name=config.QDRANT_AGENTS_COLLECTION,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
            scroll_filter=scroll_filter,
        )
        for p in results:
            all_agents.append({**p.payload, "_id": p.id})
        if offset is None:
            break
        if len(all_agents) >= limit:
            break

    return all_agents[:limit]


def get_agent_by_name(name: str, agency: str) -> dict | None:
    client = get_client()
    point_id = agent_id(name, agency)

    try:
        points = client.retrieve(
            collection_name=config.QDRANT_AGENTS_COLLECTION,
            ids=[point_id],
            with_payload=True,
            with_vectors=False,
        )
        if points:
            return {**points[0].payload, "_id": points[0].id}
    except Exception:
        pass

    results, _ = client.scroll(
        collection_name=config.QDRANT_AGENTS_COLLECTION,
        limit=10,
        with_payload=True,
        with_vectors=False,
        scroll_filter=Filter(must=[
            FieldCondition(key="name", match=MatchValue(value=name)),
            FieldCondition(key="agency", match=MatchValue(value=agency)),
        ]),
    )
    if results:
        return {**results[0].payload, "_id": results[0].id}
    return None


def get_unique_agencies() -> list[str]:
    agents = get_all_agents(limit=2000)
    return sorted(set(a.get("agency", "") for a in agents if a.get("agency")))


def get_unique_genres() -> list[str]:
    agents = get_all_agents(limit=2000)
    genres = set()
    for a in agents:
        for g in a.get("genres", []):
            if g:
                genres.add(g)
    return sorted(genres)


def get_agent_count() -> int:
    client = get_client()
    info = client.get_collection(config.QDRANT_AGENTS_COLLECTION)
    return info.points_count


def upsert_agent(agent: dict) -> None:
    from llm_client import get_embedding
    client = get_client()

    name = agent.get("name", "Unknown")
    agency = agent.get("agency", "Unknown")
    text = f"{name} at {agency} {' '.join(agent.get('genres', []))} {agent.get('bio', '')}"
    vector = get_embedding(text)

    point_id = agent_id(name, agency)
    agent["last_updated"] = agent.get("last_updated") or __import__("datetime").datetime.now().isoformat()

    client.upsert(
        collection_name=config.QDRANT_AGENTS_COLLECTION,
        points=[PointStruct(id=point_id, vector=vector, payload=agent)],
    )


def delete_agent(name: str, agency: str) -> bool:
    client = get_client()
    point_id = agent_id(name, agency)
    try:
        client.delete(
            collection_name=config.QDRANT_AGENTS_COLLECTION,
            points_selector=[point_id],
        )
        return True
    except Exception:
        return False
