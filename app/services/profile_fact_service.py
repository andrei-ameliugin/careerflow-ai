from __future__ import annotations

from collections.abc import Sequence

from app.db.models.profile_fact import ProfileFact
from app.repositories.profile_fact_repository import ProfileFactRepository


class ProfileFactService:
    def __init__(self, repository: ProfileFactRepository) -> None:
        self.repository = repository

    def list_facts(self, *, profile_id: int) -> Sequence[ProfileFact]:
        normalized_profile_id = self._validate_profile_id(profile_id)
        return self.repository.list_by_profile(normalized_profile_id)

    def _validate_profile_id(self, profile_id: int) -> int:
        if profile_id <= 0:
            raise ValueError("profile_id must be positive")
        return profile_id
