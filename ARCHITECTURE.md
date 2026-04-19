# QueryForge v2 — Architecture Plan

## Overview

Literary agent finder and query letter generator. Rebuilt from scratch to replace the monolithic 1236-line Streamlit app with a clean, modular NiceGUI application.

## UI Framework: NiceGUI

- Quasar components (production-grade tables, forms, dialogs)
- Single Docker container, FastAPI + Uvicorn backend
- Port: **12123**
- No Node.js build step required

## LLM Pipeline: 3 Agents (simplified from 9)

| Stage | What | LLM? |
|---|---|---|
| 1. Guidelines Parser | Extract structured requirements from raw guidelines per agency (cached) | YES |
| 2. Letter Writer | Write personalized paragraph(s) based on guidelines + manuscript data | YES |
| 3. Auditor | Review, grade, and suggest fixes (optional pass) | YES |

Fixed content (header, address, comps line, synopsis, bio, closing) — filled by Python, no LLM.

## Data Sources

| Source | Type | Contents | Managed By |
|---|---|---|---|
| `literary-agents` (Qdrant) | 151 agents, 90 agencies | Agent name, agency, genres, email, submission method, guidelines URL | QueryForge v2 (read/write) |
| `top-book-titles` (Qdrant) | 396 books, 13 genres | Title, author, genre, Goodreads rating/reviews, pages, year, series | qdrant-forge (read-only for QF2) |
| PostgreSQL | Structured data | Agencies, parsed guidelines, manuscripts, authors, query letters | QueryForge v2 (read/write) |

### Qdrant Collections

**`literary-agents`** — Agent data, 4096-dim cosine vectors (Qwen3-Embedding-8B)
- Agent fields: name, agency, genres, accepts_new_authors, agency_size, submission_method, response_time, sales_track_record, guidelines_url, website, bio, notes, email, twitter, last_updated, source, agency_website, location, phone, preferred_contact, source_genre, submission_guidelines_url

**`top-book-titles`** — Book database, 4096-dim cosine vectors (managed by qdrant-forge)
- Book fields: title, author, genre, goodreads_rating, goodreads_ratings_count, goodreads_reviews_count, pages, published_year, series, titling_pattern, data_source
- Genres: Literary / Magical Realism, Myth Retelling / Feminism, Regency / Gaslamp Fantasy, Dark Academia, Historical Children's Fantasy, Contemporary Fantasy, Fantasy, Feminism, Fiction, Young Adult, Young Adult Historical Fantasy, dark fantasy, witches

### Integration with qdrant-forge

1. **Comp Title Lookups** — Verify comp titles against `top-book-titles`, suggest similar books via semantic search
2. **Genre Validation** — Cross-reference manuscript genre against known genres
3. **Market Positioning** — LLM references market data in query letters (ratings, popularity)
4. **Agent-Genre Matching** — Match agents whose genres overlap with books in user's genre space

### Scraping Sources

Primary (proven): QueryTracker, AgentQuery, MSWishList, AAR Online
Secondary (to explore): Publishers Marketplace, Manuscript Wish List, etc.
Tools: SearXNG (192.168.1.169:11999), crawl4ai

## App Structure

```
query-forge-v2/
├── app.py                    # NiceGUI entry point + navigation
├── config.py                 # Settings, API keys, DB connections
├── models/
│   ├── database.py           # PostgreSQL connection + SQLAlchemy models
│   ├── qdrant_agents.py      # Qdrant `literary-agents` CRUD + search
│   ├── qdrant_books.py       # Qdrant `top-book-titles` queries (READ-ONLY)
│   ├── agency.py             # Agency CRUD (PostgreSQL)
│   ├── manuscript.py         # Manuscript CRUD (PostgreSQL)
│   ├── author.py             # Author CRUD (PostgreSQL)
│   └── query_letter.py       # Query letter CRUD (PostgreSQL)
├── pages/
│   ├── dashboard.py          # Stats, quick actions
│   ├── agents.py             # Browse/search/enrich agents
│   ├── agencies.py           # Manage agencies + parsed guidelines
│   ├── manuscripts.py        # Manuscript CRUD
│   ├── authors.py            # Author profiles
│   ├── query_letters.py      # Generate/review/export letters
│   └── scraper.py            # Run scraping/enrichment jobs
├── services/
│   ├── scraper.py            # SearXNG + crawl4ai agent scraping
│   ├── guidelines_parser.py  # LLM: parse raw guidelines → structured
│   ├── letter_writer.py      # LLM: write personalized content
│   ├── letter_auditor.py     # LLM: review + grade
│   ├── mail_merge.py         # Assemble fixed + custom content → DOCX
│   └── comp_matcher.py       # Semantic search against top-book-titles
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## PostgreSQL Schema

### Table: agencies
```
id              SERIAL PRIMARY KEY
name            VARCHAR(255) NOT NULL UNIQUE
website         TEXT
location        TEXT
size            VARCHAR(50)
guidelines_url  TEXT
guidelines_raw  TEXT
guidelines_parsed JSONB
last_scraped_at TIMESTAMP
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

### Table: authors
```
id                  SERIAL PRIMARY KEY
name                VARCHAR(255) NOT NULL
email               VARCHAR(255)
phone               VARCHAR(50)
website             TEXT
social_links        JSONB
bio                 TEXT
personal_background TEXT
created_at          TIMESTAMP DEFAULT NOW()
updated_at          TIMESTAMP DEFAULT NOW()
```

### Table: manuscripts
```
id              SERIAL PRIMARY KEY
title           VARCHAR(500) NOT NULL
genre           VARCHAR(255)
word_count      INTEGER
hook            TEXT
synopsis        TEXT
comp_title_1    VARCHAR(500)
comp_author_1   VARCHAR(255)
comp_title_2    VARCHAR(500)
comp_author_2   VARCHAR(255)
notes           TEXT
author_id       INTEGER REFERENCES authors(id)
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

### Table: query_letters
```
id              SERIAL PRIMARY KEY
manuscript_id   INTEGER REFERENCES manuscripts(id)
agent_name      VARCHAR(255)
agency_name     VARCHAR(255)
fixed_content   TEXT
custom_content  TEXT
full_letter     TEXT
grade           VARCHAR(5)
score           FLOAT
critique        JSONB
guidelines_used TEXT
model_used      VARCHAR(100)
created_at      TIMESTAMP DEFAULT NOW()
```

### Table: scraping_jobs
```
id              SERIAL PRIMARY KEY
job_type        VARCHAR(50)
status          VARCHAR(20)
parameters      JSONB
results         JSONB
started_at      TIMESTAMP
completed_at    TIMESTAMP
```

## Key Flows

### Comp Title Lookup
1. User enters manuscript genre
2. Query `top-book-titles` for books in same genre
3. Semantic search for similar titles
4. Present as "Suggested Comp Titles" with ratings/reviews

### Query Letter Generation
1. User selects manuscript + target agent(s)
2. App loads agent data from `literary-agents` (Qdrant)
3. App loads agency's parsed guidelines from PostgreSQL
4. App looks up comp titles in `top-book-titles` for market context
5. LLM writes personalized content using:
   - Agent's specific interests/bio
   - Agency's submission requirements
   - Market data for comp titles
   - Manuscript details
6. App assembles: header (fixed) + custom content (LLM) + bio (fixed) + closing (fixed)
7. Optional: Auditor grades the letter
8. Save to PostgreSQL, export as DOCX

### Agent Scraping
1. Search agent directories via SearXNG
2. Scrape pages via crawl4ai
3. LLM extracts structured agent data
4. Store in `literary-agents` Qdrant collection
5. Enrich missing fields (email, website, location) via web search

### Guidelines Scraping
1. Group agents by agency
2. Probe agency website for submission guidelines pages
3. Scrape via crawl4ai → save raw HTML
4. LLM parses into structured requirements
5. Cache parsed guidelines in PostgreSQL

## Infrastructure

- **unRAID server** at 192.168.1.169
- **Qdrant** at 192.168.1.169:6333
- **PostgreSQL 15** at 192.168.1.169:5432 (container: postgresql15, user: root, password: b42,W37k)
- **SearXNG** at 192.168.1.169:11999
- **crawl4ai** available
- **GitHub**: minisaurus org, authenticated via `gh` CLI

## LLM Models

- GLM-4.7 (Zhipu AI direct) — primary
- GLM-4.7 Flash (OpenRouter) — fast tasks
- GLM-5.1 (OpenRouter) — heavy tasks
- Embedding: Qwen3-Embedding-8B via OpenRouter (4096-dim)

## Migration from Old Version

- Qdrant `literary-agents` collection: keep as-is (151 agents)
- 20 guideline markdown files from `output/guidelines/`: import into PostgreSQL
- 1 author profile from `output/authors/`: import into PostgreSQL
- 6 manuscripts from `output/manuscripts/`: import into PostgreSQL (test data)
