from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.db.models.wizard_answer import WizardAnswer
from app.repositories.wizard_answer_repository import WizardAnswerRepository

DEEP_DIVE_QUESTION_KEY = "deep_dive"
METRICS_QUESTION_KEY = "metrics"
TOOLS_QUESTION_KEY = "tools"
SOFT_SKILLS_QUESTION_KEY = "soft_skills"

INTERVIEW_QUESTIONS: tuple[tuple[str, str], ...] = (
    (
        DEEP_DIVE_QUESTION_KEY,
        "Describe your recent career path, key projects, and achievements in detail.",
    ),
    (
        METRICS_QUESTION_KEY,
        "What measurable outcomes, metrics, or business impact should be highlighted?",
    ),
    (
        TOOLS_QUESTION_KEY,
        "Which tools, technologies, domains, or workflows best represent your experience?",
    ),
    (
        SOFT_SKILLS_QUESTION_KEY,
        "Share a challenge, setback, or difficult collaboration that shows how you work through problems.",
    ),
)


class WizardAnswerService:
    def __init__(self, repository: WizardAnswerRepository) -> None:
        self.repository = repository

    def save_deep_context_interview(
        self,
        *,
        profile_id: int,
        answers_by_key: Mapping[str, object],
    ) -> list[WizardAnswer]:
        normalized_profile_id = self._validate_profile_id(profile_id)
        normalized_answers = {
            question_key: self._normalize_optional_text(answers_by_key.get(question_key))
            for question_key, _ in INTERVIEW_QUESTIONS
        }

        if not normalized_answers[DEEP_DIVE_QUESTION_KEY]:
            raise ValueError("deep_dive answer is required")

        answer_records = [
            {
                "profile_id": normalized_profile_id,
                "question_key": question_key,
                "question_text": question_text,
                "answer_text": normalized_answers[question_key],
            }
            for question_key, question_text in INTERVIEW_QUESTIONS
            if normalized_answers[question_key]
        ]

        return self.repository.replace_answers(
            profile_id=normalized_profile_id,
            answers=answer_records,
            question_keys=[question_key for question_key, _ in INTERVIEW_QUESTIONS],
        )

    def get_answers_by_key(self, *, profile_id: int) -> dict[str, str]:
        normalized_profile_id = self._validate_profile_id(profile_id)
        saved_answers = {
            question_key: ""
            for question_key, _ in INTERVIEW_QUESTIONS
        }

        for answer in self.repository.list_by_profile(normalized_profile_id):
            if answer.question_key in saved_answers and not saved_answers[answer.question_key]:
                saved_answers[answer.question_key] = answer.answer_text

        return saved_answers

    def get_question_definitions(self) -> Sequence[tuple[str, str]]:
        return INTERVIEW_QUESTIONS

    def _validate_profile_id(self, profile_id: int) -> int:
        if profile_id <= 0:
            raise ValueError("profile_id must be positive")
        return profile_id

    def _normalize_optional_text(self, value: object) -> str:
        return str(value).strip() if value is not None else ""
