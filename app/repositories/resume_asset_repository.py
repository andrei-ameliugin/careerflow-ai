from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models.resume_asset import ResumeAsset


class ResumeAssetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_resume_asset(self, **resume_asset_data: object) -> ResumeAsset:
        resume_asset = ResumeAsset(**resume_asset_data)
        self.session.add(resume_asset)
        self.session.commit()
        self.session.refresh(resume_asset)
        return resume_asset

    def list_by_profile(self, profile_id: int) -> Sequence[ResumeAsset]:
        statement = (
            select(ResumeAsset)
            .where(ResumeAsset.profile_id == profile_id)
            .order_by(desc(ResumeAsset.created_at), desc(ResumeAsset.id))
        )
        return self.session.scalars(statement).all()

    def get_latest_by_profile(self, profile_id: int) -> ResumeAsset | None:
        statement = (
            select(ResumeAsset)
            .where(ResumeAsset.profile_id == profile_id)
            .order_by(desc(ResumeAsset.created_at), desc(ResumeAsset.id))
        )
        return self.session.scalars(statement).first()
