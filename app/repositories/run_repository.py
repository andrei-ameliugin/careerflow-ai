from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models.run import Run


class RunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, **run_data: object) -> Run:
        run = Run(**run_data)
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def list_by_profile(self, profile_id: int) -> Sequence[Run]:
        statement = (
            select(Run)
            .where(Run.profile_id == profile_id)
            .order_by(desc(Run.started_at), desc(Run.id))
        )
        return self.session.scalars(statement).all()
