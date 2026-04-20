from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import init_db
from app.repositories import ProfileRepository, RunRepository, WizardAnswerRepository
from app.services import ProfileService, RunService, WizardAnswerService
from app.services.run_service import RUN_MODE_ANALYZE_ONLY, RUN_STATUS_DRAFT
from app.services.wizard_answer_service import (
    DEEP_DIVE_QUESTION_KEY,
    TOOLS_QUESTION_KEY,
)


@pytest.fixture()
def sqlite_url(tmp_path: Path) -> str:
    database_path = tmp_path / "smoke.sqlite3"
    return f"sqlite:///{database_path}"


@pytest.fixture()
def initialized_engine(monkeypatch: pytest.MonkeyPatch, sqlite_url: str) -> Iterator[Engine]:
    import app.db.session as db_session

    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(db_session, "engine", engine)

    init_db()

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(initialized_engine: Engine) -> Iterator[Session]:
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=initialized_engine,
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_init_db_creates_expected_tables(initialized_engine: Engine) -> None:
    table_names = set(inspect(initialized_engine).get_table_names())

    assert {"profile_facts", "profiles", "resume_assets", "runs", "wizard_answers"} <= table_names


def test_create_profile_persists_to_temporary_sqlite(db_session: Session) -> None:
    service = ProfileService(ProfileRepository(db_session))

    profile = service.create_profile(
        name="Alice",
        target_title="Backend Engineer",
        hh_resume_url="https://hh.ru/resume/123",
    )

    db_session.expire_all()
    saved_profile = ProfileRepository(db_session).get_profile(profile.id)

    assert profile.id is not None
    assert saved_profile is not None
    assert saved_profile.name == "Alice"
    assert saved_profile.target_title == "Backend Engineer"
    assert saved_profile.hh_resume_url == "https://hh.ru/resume/123"


def test_save_wizard_answers_persists_to_temporary_sqlite(db_session: Session) -> None:
    profile = ProfileService(ProfileRepository(db_session)).create_profile(
        name="Alice",
        target_title="Backend Engineer",
    )
    service = WizardAnswerService(WizardAnswerRepository(db_session))

    saved_answers = service.save_deep_context_interview(
        profile_id=profile.id,
        answers_by_key={
            DEEP_DIVE_QUESTION_KEY: "Led a migration across three services.",
            TOOLS_QUESTION_KEY: "Python, SQLAlchemy, Streamlit",
        },
    )

    persisted_answers = service.list_answers(profile_id=profile.id)

    assert len(saved_answers) == 2
    assert [answer.question_key for answer in persisted_answers] == [
        TOOLS_QUESTION_KEY,
        DEEP_DIVE_QUESTION_KEY,
    ]
    assert {answer.question_key for answer in persisted_answers} == {
        DEEP_DIVE_QUESTION_KEY,
        TOOLS_QUESTION_KEY,
    }


def test_create_run_draft_persists_to_temporary_sqlite(db_session: Session) -> None:
    profile = ProfileService(ProfileRepository(db_session)).create_profile(
        name="Alice",
        target_title="Backend Engineer",
    )
    service = RunService(RunRepository(db_session))

    run = service.create_draft_run(
        profile_id=profile.id,
        mode=RUN_MODE_ANALYZE_ONLY,
    )

    persisted_runs = service.list_runs(profile_id=profile.id)

    assert run.id is not None
    assert len(persisted_runs) == 1
    assert persisted_runs[0].id == run.id
    assert persisted_runs[0].mode == RUN_MODE_ANALYZE_ONLY
    assert persisted_runs[0].status == RUN_STATUS_DRAFT
