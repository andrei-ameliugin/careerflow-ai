from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.profile import Profile


class ProfileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_profile(self, **profile_data: object) -> Profile:
        profile = Profile(**profile_data)
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def get_profile(self, profile_id: int) -> Profile | None:
        return self.session.get(Profile, profile_id)

    def list_profiles(self) -> Sequence[Profile]:
        statement = select(Profile).order_by(Profile.id)
        return self.session.scalars(statement).all()

    def update_profile(self, profile_id: int, **profile_data: object) -> Profile | None:
        profile = self.get_profile(profile_id)
        if profile is None:
            return None

        for field, value in profile_data.items():
            setattr(profile, field, value)

        self.session.commit()
        self.session.refresh(profile)
        return profile
