from __future__ import annotations

from collections.abc import Sequence

from app.core import get_logger
from app.db.models.run import Run
from app.repositories.run_repository import RunRepository

RUN_MODE_ANALYZE_ONLY = "analyze_only"
RUN_MODE_AUTO_APPLY = "auto_apply"
RUN_MODE_ASSISTED_APPLY = "assisted_apply"
RUN_STATUS_DRAFT = "draft"

SUPPORTED_RUN_MODES = (
    RUN_MODE_ANALYZE_ONLY,
    RUN_MODE_AUTO_APPLY,
    RUN_MODE_ASSISTED_APPLY,
)

logger = get_logger(__name__)


class RunService:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    def create_draft_run(self, *, profile_id: int, mode: object) -> Run:
        normalized_profile_id = self._validate_profile_id(profile_id)
        normalized_mode = self._validate_mode(mode)
        run = self.repository.create_run(
            profile_id=normalized_profile_id,
            mode=normalized_mode,
            status=RUN_STATUS_DRAFT,
        )
        logger.info(
            "Created draft run id=%s profile_id=%s mode=%s status=%s",
            run.id,
            run.profile_id,
            run.mode,
            run.status,
        )
        return run

    def list_runs(self, *, profile_id: int) -> Sequence[Run]:
        normalized_profile_id = self._validate_profile_id(profile_id)
        return self.repository.list_by_profile(normalized_profile_id)

    def _validate_profile_id(self, profile_id: int) -> int:
        if profile_id <= 0:
            raise ValueError("profile_id must be positive")
        return profile_id

    def _validate_mode(self, mode: object) -> str:
        normalized_mode = str(mode).strip() if mode is not None else ""
        if normalized_mode not in SUPPORTED_RUN_MODES:
            supported_modes = ", ".join(SUPPORTED_RUN_MODES)
            raise ValueError(f"mode must be one of: {supported_modes}")
        return normalized_mode
