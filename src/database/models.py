from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)  # null for OAuth-only users
    provider = Column(String(20), nullable=True)  # e.g., 'google', 'github'
    provider_id = Column(String(100), nullable=True)
    fcm_token = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(String(64), primary_key=True)  # accept any string UUID
    game_type = Column(String(50), nullable=False)
    player_white = Column(String(100), nullable=True)
    player_black = Column(String(100), nullable=True)
    player_white_id = Column(Integer, nullable=True)
    player_black_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default="in_progress")

    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(64), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    turn = Column(Integer, nullable=False)
    player = Column(String(50), nullable=False)
    action = Column(Text, nullable=False)
    new_state = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="events")