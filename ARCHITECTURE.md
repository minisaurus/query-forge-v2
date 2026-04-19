# QueryForge v2 — Status

## Overview

Literary agent finder and query letter generator. Rebuilt from scratch to replace the monolithic 1236-line Streamlit app with a clean, modular NiceGUI application.

**Status: PAUSED** — App is live and functional, scraping pipeline needs to be wired up.

**Live at:** http://192.168.1.169:12123

## What's Built

### UI (NiceGUI + Quasar)
- 7 pages: Dashboard, Agents, Agencies, Manuscripts, Authors, Query Letters, Scraper
- Pagination on Agents page (20 per page)
- Copy-to-clipboard button on agent emails
- All pages returning HTTP 200

### Backend
- PostgreSQL `queryforge` database (5 tables: agencies, authors, manuscripts, query_letters, scraping_jobs)
- Qdrant `literary-agents` collection: 151 agents, 90 agencies (read/write)
- Qdrant `top-book-titles` collection: 396 books, 13 genres (read-only, from qdrant-forge)
- SQLAlchemy ORM for all PostgreSQL operations

### Services (code complete, untested end-to-end)
- `guidelines_parser.py` — LLM parses raw guidelines into structured JSON
- `letter_writer.py` — LLM writes personalized query letter body
- `letter_auditor.py` — LLM grades letter (8 criteria, A+ to F)
- `mail_merge.py` — Assembles fixed content + LLM content into final letter
- `comp_matcher.py` — Semantic search against qdrant-forge for comp title lookups
- `llm_client.py` — GLM-4.7 + OpenRouter embedding

### Docker
- Single container on port 12123, `network_mode: host`
- Image: `query-forge-v2-query-forge-v2`

## What Needs Work

### High Priority
- **Scraper pipeline** — The Scraper page UI is a shell with placeholder functions. Needs to be wired up to:
  - `searxng_client.py` — Search agent directories
  - `crawl4ai_client.py` — Scrape pages
  - Agent extraction from scraped pages via LLM
  - Store results in Qdrant

### Medium Priority
- **Query letter generation** — Code is complete but hasn't been tested with real manuscripts
- **Guidelines sync** — Store/retrieve parsed guidelines from PostgreSQL
- **DOCX export** — Add export-to-Word for query letters
- **Agent enrichment** — Fill missing agent data (email, website, location) via web search

### Nice to Have
- Authentication (login to protect data)
- Agent filtering by multiple genres
- Manuscript version history (track edits over time)
- Bulk query letter generation (select multiple agents)

## Architecture

```
query-forge-v2/
├── app.py                    # NiceGUI entry point + 7 page routes
├── config.py                 # Config from .env
├── models/
│   ├── database.py          # SQLAlchemy models + engine
│   ├── qdrant_agents.py      # literary-agents CRUD + semantic search
│   └── qdrant_books.py       # top-book-titles queries (read-only)
├── pages/
│   ├── dashboard.py          # Stats overview
│   ├── agents.py             # Browse/search agents (Qdrant)
│   ├── agencies.py          # List agencies + guidelines status
│   ├── manuscripts.py        # Manuscript CRUD + comp suggestions
│   ├── authors.py            # Author CRUD
│   ├── query_letters.py      # Generate letters
│   └── scraper.py            # Scraping job runner (placeholder)
└── services/
    ├── llm_client.py        # GLM-4.7 + OpenRouter embedding
    ├── guidelines_parser.py  # LLM: raw → structured guidelines
    ├── letter_writer.py      # LLM: personalized query content
    ├── letter_auditor.py     # LLM: grade + critique
    ├── mail_merge.py         # Assemble final letter
    └── comp_matcher.py       # Comp title lookup
```

## Data Schema

### PostgreSQL Tables

**agencies** — name (PK), website, location, size, guidelines_url, guidelines_raw, guidelines_parsed (JSONB), last_scraped_at, created_at, updated_at

**authors** — id (PK), name, email, phone, website, social_links (JSONB), bio, personal_background, created_at, updated_at

**manuscripts** — id (PK), title, genre, word_count, hook, synopsis, comp_title_1/2, comp_author_1/2, notes, author_id (FK), created_at, updated_at

**query_letters** — id (PK), manuscript_id (FK), agent_name, agency_name, fixed_content, custom_content, full_letter, grade, score, critique (JSONB), guidelines_used, model_used, created_at

**scraping_jobs** — id (PK), job_type, status, parameters (JSONB), results (JSONB), started_at, completed_at

### Qdrant Collections

**literary-agents** — 4096-dim cosine, point ID = MD5(name@agency)
- Fields: name, agency, genres[], accepts_new_authors, agency_size, submission_method, response_time, bio, notes, email, twitter, website, agency_website, location, phone, preferred_contact, guidelines_url, submission_guidelines_url, source, last_updated

**top-book-titles** (qdrant-forge, read-only) — 4096-dim cosine
- Fields: title, author, genre, goodreads_rating, goodreads_ratings_count, goodreads_reviews_count, pages, published_year, series, titling_pattern, data_source

## Infrastructure

| Service | Host | Port |
|---|---|---|
| QueryForge v2 | 192.168.1.169 | 12123 |
| Qdrant | 192.168.1.169 | 6333 |
| PostgreSQL 15 | 192.168.1.169 | 5432 |
| SearXNG | 192.168.1.169 | 11999 |
| crawl4ai | 192.168.1.169 | 11235 |

## GitHub

https://github.com/minisaurus/query-forge-v2

Branches: master
