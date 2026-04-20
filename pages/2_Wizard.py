from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from app.db import SessionLocal, init_db
from app.db.models.profile import Profile
from app.repositories import ProfileRepository
from app.services import ProfileService


def load_profiles() -> Sequence[Profile]:
    init_db()
    session = SessionLocal()
    try:
        service = ProfileService(ProfileRepository(session))
        return service.list_profiles()
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
    st.caption(
        "Stub layout for choosing how resume content will be provided for the selected profile."
    )

    left_column, right_column = st.columns([1, 1])

    with left_column:
        st.text_input(
            "Resume URL",
            value=selected_profile.hh_resume_url,
            placeholder="https://hh.ru/resume/...",
            disabled=True,
        )
        st.file_uploader(
            "Resume file",
            type=["pdf", "doc", "docx", "txt"],
            disabled=True,
        )

    with right_column:
        st.text_area(
            "Resume text",
            placeholder="Paste resume text here",
            height=220,
            disabled=True,
        )

    st.info("Resume import controls are placeholders for now.")
    st.button("Continue to Experience Questions", disabled=True)


def render_experience_questions_step() -> None:
    st.subheader("Step 2: Experience Questions")
    st.caption("Stub layout for guided questions that enrich the selected profile.")

    with st.container(border=True):
        st.markdown("**Question 1**")
        st.text_area(
            "Describe a project or achievement you want highlighted.",
            height=100,
            disabled=True,
        )

    with st.container(border=True):
        st.markdown("**Question 2**")
        st.text_area(
            "What tools, domains, or responsibilities should be emphasized?",
            height=100,
            disabled=True,
        )

    st.info("Question flow and saving are placeholders for now.")
    action_column, secondary_column = st.columns(2)
    with action_column:
        st.button("Save Draft", disabled=True)
    with secondary_column:
        st.button("Generate Next Questions", disabled=True)


def main() -> None:
    st.title("Wizard")
    st.caption("Select a profile and walk through resume input and experience questions.")

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
    render_experience_questions_step()


if __name__ == "__main__":
    main()
