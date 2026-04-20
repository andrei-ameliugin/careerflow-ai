from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from app.db.models.wizard_answer import WizardAnswer


class WizardAnswerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_wizard_answer(self, **wizard_answer_data: object) -> WizardAnswer:
        wizard_answer = WizardAnswer(**wizard_answer_data)
        self.session.add(wizard_answer)
        self.session.commit()
        self.session.refresh(wizard_answer)
        return wizard_answer

    def replace_answers(
        self,
        *,
        profile_id: int,
        answers: Sequence[dict[str, object]],
        question_keys: Sequence[str],
    ) -> list[WizardAnswer]:
        self.session.execute(
            delete(WizardAnswer).where(
                WizardAnswer.profile_id == profile_id,
                WizardAnswer.question_key.in_(question_keys),
            )
        )

        created_answers: list[WizardAnswer] = []
        for answer_data in answers:
            wizard_answer = WizardAnswer(**answer_data)
            self.session.add(wizard_answer)
            created_answers.append(wizard_answer)

        self.session.commit()

        for wizard_answer in created_answers:
            self.session.refresh(wizard_answer)

        return created_answers

    def list_by_profile(self, profile_id: int) -> Sequence[WizardAnswer]:
        statement = (
            select(WizardAnswer)
            .where(WizardAnswer.profile_id == profile_id)
            .order_by(desc(WizardAnswer.created_at), desc(WizardAnswer.id))
        )
        return self.session.scalars(statement).all()
