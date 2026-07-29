# ==========================================
# database.py
# SQLAlchemy Database Configuration
# ==========================================

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship
)

from app.config import DATABASE_URL


# ------------------------------------------
# Create Database Engine
# ------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# ------------------------------------------
# Create Session
# ------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ------------------------------------------
# Base Class
# ------------------------------------------

Base = declarative_base()


# ==========================================
# Resume Table
# ==========================================

class Resume(Base):

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    education = Column(String)

    experience = Column(Float)

    skills = Column(Text)

    location = Column(String)

    category = Column(String)

    resume_text = Column(Text)

    file_name = Column(String)


# ==========================================
# Job Table
# ==========================================

class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)

    description = Column(Text)

    required_skills = Column(Text)

    experience = Column(Float)

    education = Column(String)

    location = Column(String)

    


# ==========================================
# Chat Session Table
# ==========================================

class Session(Base):

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    conversations = relationship(
        "Conversation",
        back_populates="session",
        cascade="all, delete"
    )


# ==========================================
# Conversation Table
# ==========================================

class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id")
    )

    role = Column(String)

    message = Column(Text)

    session = relationship(
        "Session",
        back_populates="conversations"
    )


# ------------------------------------------
# Create Tables
# ------------------------------------------

Base.metadata.create_all(bind=engine)