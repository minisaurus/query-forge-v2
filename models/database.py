import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import config

engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    website = Column(Text)
    location = Column(Text)
    size = Column(String(50))
    guidelines_url = Column(Text)
    guidelines_raw = Column(Text)
    guidelines_parsed = Column(JSON)
    last_scraped_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(Text)
    social_links = Column(JSON)
    bio = Column(Text)
    personal_background = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    manuscripts = relationship("Manuscript", back_populates="author_rel")


class Manuscript(Base):
    __tablename__ = "manuscripts"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    genre = Column(String(255))
    word_count = Column(Integer)
    hook = Column(Text)
    synopsis = Column(Text)
    comp_title_1 = Column(String(500))
    comp_author_1 = Column(String(255))
    comp_title_2 = Column(String(500))
    comp_author_2 = Column(String(255))
    notes = Column(Text)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author_rel = relationship("Author", back_populates="manuscripts")
    query_letters = relationship("QueryLetter", back_populates="manuscript_rel", cascade="all, delete-orphan")


class QueryLetter(Base):
    __tablename__ = "query_letters"

    id = Column(Integer, primary_key=True)
    manuscript_id = Column(Integer, ForeignKey("manuscripts.id"), nullable=False)
    agent_name = Column(String(255))
    agency_name = Column(String(255))
    fixed_content = Column(Text)
    custom_content = Column(Text)
    full_letter = Column(Text)
    grade = Column(String(5))
    score = Column(Float)
    critique = Column(JSON)
    guidelines_used = Column(Text)
    model_used = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

    manuscript_rel = relationship("Manuscript", back_populates="query_letters")


class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True)
    job_type = Column(String(50))
    status = Column(String(20), default="pending")
    parameters = Column(JSON)
    results = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
