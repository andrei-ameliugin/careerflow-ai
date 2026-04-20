from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models.profile_fact import ProfileFact


class ProfileFactRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_profile(self, profile_id: int) -> Sequence[ProfileFact]:
        statement = (
            select(ProfileFact)
            .where(ProfileFact.profile_id == profile_id)
            .order_by(desc(ProfileFact.created_at), desc(ProfileFact.id))
        )
        return self.session.scalars(statement).all()
