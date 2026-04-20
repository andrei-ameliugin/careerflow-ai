from __future__ import annotations

import pytest

from app.db.models.profile_fact import ProfileFact
from app.services.profile_fact_service import ProfileFactService


class FakeProfileFactRepository:
    def __init__(self) -> None:
        self.facts: list[ProfileFact] = []

    def list_by_profile(self, profile_id: int) -> list[ProfileFact]:
        return [fact for fact in self.facts if fact.profile_id == profile_id]


def test_list_facts_requires_positive_profile_id() -> None:
    service = ProfileFactService(FakeProfileFactRepository())

    with pytest.raises(ValueError, match="profile_id must be positive"):
        service.list_facts(profile_id=0)


def test_list_facts_returns_repository_results() -> None:
    repository = FakeProfileFactRepository()
    repository.facts = [
        ProfileFact(profile_id=2, fact_type="summary", title="Key Strength", content="Strong backend ownership"),
        ProfileFact(profile_id=3, fact_type="summary", title="Other", content="Ignored"),
    ]
    service = ProfileFactService(repository)

    facts = service.list_facts(profile_id=2)

    assert [fact.title for fact in facts] == ["Key Strength"]
