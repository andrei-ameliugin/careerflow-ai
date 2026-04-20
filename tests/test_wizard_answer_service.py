from __future__ import annotations

import pytest

from app.db.models.wizard_answer import WizardAnswer
from app.services.wizard_answer_service import (
    DEEP_DIVE_QUESTION_KEY,
    INTERVIEW_QUESTIONS,
    METRICS_QUESTION_KEY,
    SOFT_SKILLS_QUESTION_KEY,
    TOOLS_QUESTION_KEY,
    WizardAnswerService,
)


class FakeWizardAnswerRepository:
    def __init__(self) -> None:
        self.answers: list[WizardAnswer] = []
        self.replace_calls: list[dict[str, object]] = []

    def replace_answers(
        self,
        *,
        profile_id: int,
        answers: list[dict[str, object]],
        question_keys: list[str],
    ) -> list[WizardAnswer]:
        self.replace_calls.append(
            {
                "profile_id": profile_id,
                "answers": answers,
                "question_keys": question_keys,
            }
        )
        self.answers = [
            WizardAnswer(**answer_data)
            for answer_data in answers
        ]
        return self.answers

    def list_by_profile(self, profile_id: int) -> list[WizardAnswer]:
        return [answer for answer in self.answers if answer.profile_id == profile_id]


def test_save_deep_context_interview_requires_q1() -> None:
    service = WizardAnswerService(FakeWizardAnswerRepository())

    with pytest.raises(ValueError, match="deep_dive answer is required"):
        service.save_deep_context_interview(
            profile_id=1,
            answers_by_key={DEEP_DIVE_QUESTION_KEY: "   "},
        )


def test_save_deep_context_interview_skips_empty_optional_answers() -> None:
    repository = FakeWizardAnswerRepository()
    service = WizardAnswerService(repository)

    saved_answers = service.save_deep_context_interview(
        profile_id=4,
        answers_by_key={
            DEEP_DIVE_QUESTION_KEY: "Led platform migration",
            METRICS_QUESTION_KEY: "  ",
            TOOLS_QUESTION_KEY: "Python, SQLAlchemy, Streamlit",
            SOFT_SKILLS_QUESTION_KEY: "",
        },
    )

    assert [answer.question_key for answer in saved_answers] == [
        DEEP_DIVE_QUESTION_KEY,
        TOOLS_QUESTION_KEY,
    ]
    assert repository.replace_calls[0]["question_keys"] == [
        question_key for question_key, _ in INTERVIEW_QUESTIONS
    ]


def test_get_answers_by_key_returns_defaults_for_missing_questions() -> None:
    repository = FakeWizardAnswerRepository()
    service = WizardAnswerService(repository)
    repository.answers = [
        WizardAnswer(
            profile_id=8,
            question_key=DEEP_DIVE_QUESTION_KEY,
            question_text="Deep dive",
            answer_text="Built internal tools",
        )
    ]

    answers = service.get_answers_by_key(profile_id=8)

    assert answers[DEEP_DIVE_QUESTION_KEY] == "Built internal tools"
    assert answers[METRICS_QUESTION_KEY] == ""
    assert answers[TOOLS_QUESTION_KEY] == ""
    assert answers[SOFT_SKILLS_QUESTION_KEY] == ""


def test_list_answers_requires_positive_profile_id() -> None:
    service = WizardAnswerService(FakeWizardAnswerRepository())

    with pytest.raises(ValueError, match="profile_id must be positive"):
        service.list_answers(profile_id=0)


def test_list_answers_returns_repository_results() -> None:
    repository = FakeWizardAnswerRepository()
    repository.answers = [
        WizardAnswer(
            profile_id=8,
            question_key=DEEP_DIVE_QUESTION_KEY,
            question_text="Deep dive",
            answer_text="Built internal tools",
        ),
        WizardAnswer(
            profile_id=9,
            question_key=TOOLS_QUESTION_KEY,
            question_text="Tools",
            answer_text="Python",
        ),
    ]
    service = WizardAnswerService(repository)

    answers = service.list_answers(profile_id=8)

    assert [answer.question_key for answer in answers] == [DEEP_DIVE_QUESTION_KEY]
