from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from app.db import SessionLocal, init_db
from app.db.models.profile import Profile
from app.db.models.resume_asset import ResumeAsset
from app.db.models.wizard_answer import WizardAnswer
from app.repositories import ProfileRepository
from app.repositories.resume_asset_repository import ResumeAssetRepository
from app.repositories.wizard_answer_repository import WizardAnswerRepository
from app.services import ProfileService, ResumeAssetService, WizardAnswerService
from app.services.wizard_answer_service import (
    DEEP_DIVE_QUESTION_KEY,
    INTERVIEW_QUESTIONS,
    METRICS_QUESTION_KEY,
    SOFT_SKILLS_QUESTION_KEY,
    TOOLS_QUESTION_KEY,
)


def load_profiles() -> Sequence[Profile]:
    init_db()
    session = SessionLocal()
    try:
        service = ProfileService(ProfileRepository(session))
        return service.list_profiles()
    finally:
        session.close()


def save_pasted_resume(*, profile_id: int, raw_text: str) -> ResumeAsset:
    init_db()
    session = SessionLocal()
    try:
        service = ResumeAssetService(ResumeAssetRepository(session))
        return service.save_pasted_text(profile_id=profile_id, raw_text=raw_text)
    finally:
        session.close()


def save_uploaded_resume(*, profile_id: int, filename: str, file_bytes: bytes) -> ResumeAsset:
    init_db()
    session = SessionLocal()
    try:
        service = ResumeAssetService(ResumeAssetRepository(session))
        return service.save_uploaded_file(
            profile_id=profile_id,
            filename=filename,
            file_bytes=file_bytes,
        )
    finally:
        session.close()


def load_latest_resume_asset(*, profile_id: int) -> ResumeAsset | None:
    init_db()
    session = SessionLocal()
    try:
        service = ResumeAssetService(ResumeAssetRepository(session))
        return service.get_latest_asset(profile_id=profile_id)
    finally:
        session.close()


def save_deep_context_interview(
    *,
    profile_id: int,
    answers_by_key: dict[str, str],
) -> list[WizardAnswer]:
    init_db()
    session = SessionLocal()
    try:
        service = WizardAnswerService(WizardAnswerRepository(session))
        return service.save_deep_context_interview(
            profile_id=profile_id,
            answers_by_key=answers_by_key,
        )
    finally:
        session.close()


def load_interview_answers(*, profile_id: int) -> dict[str, str]:
    init_db()
    session = SessionLocal()
    try:
        service = WizardAnswerService(WizardAnswerRepository(session))
        return service.get_answers_by_key(profile_id=profile_id)
    finally:
        session.close()


def format_profile_option(profile: Profile) -> str:
    return f"{profile.name} - {profile.target_title}"


def render_step_header(*, current_step: int) -> None:
    step_one_label = "1. Resume Input"
    step_two_label = "2. Experience Questions"

    step_one_state = "Current" if current_step == 1 else "Next"
    step_two_state = "Current" if current_step == 2 else "Upcoming"

    first_column, second_column = st.columns(2)
    with first_column:
        st.markdown(f"**{step_one_label}**")
        st.caption(step_one_state)
    with second_column:
        st.markdown(f"**{step_two_label}**")
        st.caption(step_two_state)


def render_resume_input_step(selected_profile: Profile) -> None:
    st.subheader("Step 1: Resume Input")
    st.caption("Provide resume content by pasting text or uploading a file.")

    input_method = st.radio(
        "Resume source",
        options=["Paste text", "Upload file"],
        horizontal=True,
    )

    if input_method == "Paste text":
        with st.form("resume_text_form"):
            raw_text = st.text_area(
                "Resume text",
                placeholder="Paste resume text here",
                height=240,
            )
            submitted = st.form_submit_button("Save Resume Text")

        if submitted:
            try:
                save_pasted_resume(
                    profile_id=selected_profile.id,
                    raw_text=raw_text,
                )
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state["wizard_success_message"] = "Resume text saved."
                st.rerun()
    else:
        with st.form("resume_upload_form"):
            uploaded_file = st.file_uploader(
                "Resume file",
                type=["pdf", "doc", "docx", "txt"],
            )
            submitted = st.form_submit_button("Save Uploaded Resume")

        if submitted:
            if uploaded_file is None:
                st.error("Please choose a file to upload.")
            else:
                try:
                    save_uploaded_resume(
                        profile_id=selected_profile.id,
                        filename=uploaded_file.name,
                        file_bytes=uploaded_file.getvalue(),
                    )
                except ValueError as error:
                    st.error(str(error))
                else:
                    st.session_state["wizard_success_message"] = (
                        "Resume file saved. Text extraction is currently available for .txt files only."
                    )
                    st.rerun()

    latest_asset = load_latest_resume_asset(profile_id=selected_profile.id)
    if latest_asset is None:
        st.info("No resume asset saved for this profile yet.")
    else:
        with st.container(border=True):
            st.markdown("**Latest Saved Resume Asset**")
            st.write(f"Source type: {latest_asset.source_type}")
            st.write(f"File path: {latest_asset.file_path or 'Not applicable'}")
            st.write(
                "Raw text preview: "
                + (latest_asset.raw_text[:200] if latest_asset.raw_text else "No extracted text yet")
            )

    st.button("Continue to Experience Questions", disabled=True)


def render_experience_questions_step(selected_profile: Profile) -> None:
    st.subheader("Step 2: Experience Questions")
    st.caption(
        "Use a prose-first interview. Question 1 is the primary narrative and should be as detailed as possible."
    )

    existing_answers = load_interview_answers(profile_id=selected_profile.id)

    with st.form(f"deep_context_interview_form_{selected_profile.id}"):
        st.markdown("**Question 1: The Deep Dive**")
        deep_dive_answer = st.text_area(
            "Describe your recent career path, key projects, and achievements in detail.",
            value=existing_answers[DEEP_DIVE_QUESTION_KEY],
            height=320,
            placeholder=(
                "Walk through your recent roles, major projects, concrete achievements, scope of responsibility, "
                "and the outcomes you are most proud of. The more detail you include here, the stronger the digital twin context will be."
            ),
        )

        st.markdown("**Question 2: Metrics and Impact (Optional)**")
        metrics_answer = st.text_area(
            "Add measurable outcomes, KPIs, revenue/cost impact, scale, or performance improvements that may have been missed above.",
            value=existing_answers[METRICS_QUESTION_KEY],
            height=140,
        )

        st.markdown("**Question 3: Tools and Domain Context (Optional)**")
        tools_answer = st.text_area(
            "List the tools, technologies, domains, workflows, or environments that best represent your experience.",
            value=existing_answers[TOOLS_QUESTION_KEY],
            height=140,
        )

        st.markdown("**Question 4: Challenge or Failure Story (Optional)**")
        soft_skills_answer = st.text_area(
            "Share a challenge, mistake, setback, or difficult collaboration and how you handled it.",
            value=existing_answers[SOFT_SKILLS_QUESTION_KEY],
            height=140,
        )

        can_save = bool(deep_dive_answer.strip())
        submitted = st.form_submit_button(
            "Save Deep Context Interview",
            disabled=not can_save,
        )

    if not existing_answers[DEEP_DIVE_QUESTION_KEY]:
        st.info("Question 1 is required before this interview can be considered complete.")

    if submitted:
        try:
            saved_answers = save_deep_context_interview(
                profile_id=selected_profile.id,
                answers_by_key={
                    DEEP_DIVE_QUESTION_KEY: deep_dive_answer,
                    METRICS_QUESTION_KEY: metrics_answer,
                    TOOLS_QUESTION_KEY: tools_answer,
                    SOFT_SKILLS_QUESTION_KEY: soft_skills_answer,
                },
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["wizard_success_message"] = (
                f"Deep context interview saved with {len(saved_answers)} answer(s)."
            )
            st.rerun()

    latest_answers = load_interview_answers(profile_id=selected_profile.id)
    answered_count = sum(1 for answer in latest_answers.values() if answer)
    with st.container(border=True):
        st.markdown("**Interview Status**")
        st.write(f"Saved answers: {answered_count} of {len(INTERVIEW_QUESTIONS)}")
        st.write(
            "Question 1 complete: "
            + ("Yes" if latest_answers[DEEP_DIVE_QUESTION_KEY] else "No")
        )


def main() -> None:
    st.title("Wizard")
    st.caption("Select a profile and walk through resume input and experience questions.")

    success_message = st.session_state.pop("wizard_success_message", None)
    if success_message:
        st.success(success_message)

    profiles = load_profiles()
    if not profiles:
        st.info("Create a profile on the Profiles page before using the wizard.")
        return

    selected_profile = st.selectbox(
        "Profile",
        options=profiles,
        format_func=format_profile_option,
    )

    with st.container(border=True):
        st.markdown("**Selected Profile**")
        summary_column, status_column = st.columns([3, 1])
        with summary_column:
            st.write(f"Name: {selected_profile.name}")
            st.write(f"Target title: {selected_profile.target_title}")
            st.write(
                "Resume URL: "
                + (selected_profile.hh_resume_url or "Not provided")
            )
        with status_column:
            st.write(f"Profile ID: {selected_profile.id}")
            st.write(f"Active: {'Yes' if selected_profile.is_active else 'No'}")

    render_step_header(current_step=1)
    render_resume_input_step(selected_profile)

    st.divider()

    render_step_header(current_step=2)
    render_experience_questions_step(selected_profile)


if __name__ == "__main__":
    main()
