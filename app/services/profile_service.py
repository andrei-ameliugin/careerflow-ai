from __future__ import annotations

from collections.abc import Sequence

from app.db.models.profile import Profile
from app.repositories import ProfileRepository


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
        return self.repository.create_profile(**profile_data)

    def list_profiles(self) -> Sequence[Profile]:
        return self.repository.list_profiles()

    def _validate_required_text(self, field_name: str, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError(f"{field_name} is required")
        return text

    def _normalize_hh_resume_url(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()
