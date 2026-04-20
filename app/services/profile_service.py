from __future__ import annotations

from collections.abc import Sequence

from app.core import get_logger
from app.db.models.profile import Profile
from app.repositories import ProfileRepository


logger = get_logger(__name__)


class ProfileService:
    def __init__(self, repository: ProfileRepository) -> None:
        self.repository = repository

    def create_profile(
        self,
        *,
        name: object,
        target_title: object,
        hh_resume_url: object = "",
        is_active: bool = True,
    ) -> Profile:
        profile_data = {
            "name": self._validate_required_text("name", name),
            "target_title": self._validate_required_text("target_title", target_title),
            "hh_resume_url": self._normalize_hh_resume_url(hh_resume_url),
            "is_active": is_active,
        }
        profile = self.repository.create_profile(**profile_data)
        logger.info(
            "Created profile id=%s name=%s target_title=%s is_active=%s",
            profile.id,
            profile.name,
            profile.target_title,
            profile.is_active,
        )
        return profile

    def list_profiles(self) -> Sequence[Profile]:
        return self.repository.list_profiles()

    def get_profile(self, *, profile_id: int) -> Profile | None:
        if profile_id <= 0:
            raise ValueError("profile_id must be positive")
        return self.repository.get_profile(profile_id)

    def _validate_required_text(self, field_name: str, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError(f"{field_name} is required")
        return text

    def _normalize_hh_resume_url(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()
