from __future__ import annotations

import pytest

from app.db.models.run import Run
from app.services.run_service import (
    RUN_MODE_ANALYZE_ONLY,
    RUN_STATUS_DRAFT,
    RunService,
)


class FakeRunRepository:
    def __init__(self) -> None:
        self.runs: list[Run] = []
        self.created_runs: list[dict[str, object]] = []

    def create_run(self, **run_data: object) -> Run:
        self.created_runs.append(run_data)
        run = Run(**run_data)
        self.runs.append(run)
        return run

    def list_by_profile(self, profile_id: int) -> list[Run]:
        return [run for run in self.runs if run.profile_id == profile_id]


def test_create_draft_run_requires_positive_profile_id() -> None:
    service = RunService(FakeRunRepository())

    with pytest.raises(ValueError, match="profile_id must be positive"):
        service.create_draft_run(profile_id=0, mode=RUN_MODE_ANALYZE_ONLY)


def test_create_draft_run_rejects_unsupported_mode() -> None:
    service = RunService(FakeRunRepository())

    with pytest.raises(ValueError, match="mode must be one of:"):
        service.create_draft_run(profile_id=1, mode="manual")


def test_create_draft_run_sets_draft_status() -> None:
    repository = FakeRunRepository()
    service = RunService(repository)

    run = service.create_draft_run(
        profile_id=7,
        mode=f" {RUN_MODE_ANALYZE_ONLY} ",
    )

    assert run.profile_id == 7
    assert run.mode == RUN_MODE_ANALYZE_ONLY
    assert run.status == RUN_STATUS_DRAFT
    assert repository.created_runs[0]["status"] == RUN_STATUS_DRAFT


def test_list_runs_returns_repository_results() -> None:
    repository = FakeRunRepository()
    service = RunService(repository)
    kept_run = service.create_draft_run(profile_id=3, mode=RUN_MODE_ANALYZE_ONLY)
    service.create_draft_run(profile_id=4, mode=RUN_MODE_ANALYZE_ONLY)

    assert service.list_runs(profile_id=3) == [kept_run]
