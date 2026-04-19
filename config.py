import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


class Config:
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
    ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4.7")

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_EMBED_MODEL = os.getenv("OPENROUTER_EMBED_MODEL", "qwen/qwen3-embedding-8b")

    QDRANT_HOST = os.getenv("QDRANT_HOST", "172.17.0.11")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_AGENTS_COLLECTION = os.getenv("QDRANT_AGENTS_COLLECTION", "literary-agents")
    QDRANT_BOOKS_COLLECTION = os.getenv("QDRANT_BOOKS_COLLECTION", "top-book-titles")

    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "192.168.1.169")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "root")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "queryforge")

    SEARXNG_URL = os.getenv("SEARXNG_URL", "http://192.168.1.169:11999")
    CRAWL4AI_URL = os.getenv("CRAWL4AI_URL", "http://192.168.1.169:11235")

    QUERYTRACKER_USERNAME = os.getenv("QUERYTRACKER_USERNAME", "")
    QUERYTRACKER_PASSWORD = os.getenv("QUERYTRACKER_PASSWORD", "")

    APP_PORT = int(os.getenv("APP_PORT", "12123"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @classmethod
    def validate(cls) -> list[str]:
        issues = []
        if not cls.ZHIPU_API_KEY:
            issues.append("ZHIPU_API_KEY is missing")
        if not cls.OPENROUTER_API_KEY:
            issues.append("OPENROUTER_API_KEY is missing")
        return issues


config = Config()
