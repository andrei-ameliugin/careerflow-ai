from __future__ import annotations

import pytest

from app.db.models.profile import Profile
from app.services import ProfileService


class FakeProfileRepository:
    def __init__(self) -> None:
        self.created_profiles: list[dict[str, object]] = []
        self.profiles: list[Profile] = []

    def create_profile(self, **profile_data: object) -> Profile:
        self.created_profiles.append(profile_data)
        profile = Profile(**profile_data)
        self.profiles.append(profile)
        return profile

    def list_profiles(self) -> list[Profile]:
        return self.profiles

    def get_profile(self, profile_id: int) -> Profile | None:
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        return None


def test_create_profile_validates_required_fields() -> None:
    service = ProfileService(FakeProfileRepository())

    with pytest.raises(ValueError, match="name is required"):
        service.create_profile(name="   ", target_title="Python Developer")

    with pytest.raises(ValueError, match="target_title is required"):
        service.create_profile(name="Alice", target_title=None)


def test_create_profile_normalizes_hh_resume_url() -> None:
    repository = FakeProfileRepository()
    service = ProfileService(repository)

    profile = service.create_profile(
        name=" Alice ",
        target_title=" Backend Engineer ",
        hh_resume_url=" https://hh.ru/resume/123 ",
    )

    assert profile.name == "Alice"
    assert profile.target_title == "Backend Engineer"
    assert profile.hh_resume_url == "https://hh.ru/resume/123"
    assert repository.created_profiles[0]["hh_resume_url"] == "https://hh.ru/resume/123"


def test_create_profile_allows_empty_hh_resume_url() -> None:
    service = ProfileService(FakeProfileRepository())

    profile = service.create_profile(
        name="Alice",
        target_title="Backend Engineer",
        hh_resume_url=None,
    )

    assert profile.hh_resume_url == ""


def test_list_profiles_returns_repository_results() -> None:
    repository = FakeProfileRepository()
    service = ProfileService(repository)

    created_profile = service.create_profile(
        name="Alice",
        target_title="Backend Engineer",
    )

    assert service.list_profiles() == [created_profile]


def test_get_profile_requires_positive_id() -> None:
    service = ProfileService(FakeProfileRepository())

    with pytest.raises(ValueError, match="profile_id must be positive"):
        service.get_profile(profile_id=0)


def test_get_profile_returns_repository_result() -> None:
    repository = FakeProfileRepository()
    service = ProfileService(repository)
    created_profile = service.create_profile(
        name="Alice",
        target_title="Backend Engineer",
    )
    created_profile.id = 5

    assert service.get_profile(profile_id=5) is created_profile
