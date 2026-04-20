from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

import streamlit as st

from app.db import SessionLocal, init_db
from app.db.models.profile import Profile
from app.db.models.profile_fact import ProfileFact
from app.db.models.resume_asset import ResumeAsset
from app.db.models.run import Run
from app.db.models.wizard_answer import WizardAnswer
from app.repositories import (
    ProfileFactRepository,
    ProfileRepository,
    ResumeAssetRepository,
    RunRepository,
    WizardAnswerRepository,
)
from app.services import (
    ProfileFactService,
    ProfileService,
    ResumeAssetService,
    RunService,
    WizardAnswerService,
)
from app.services.run_service import SUPPORTED_RUN_MODES


def load_profiles() -> Sequence[Profile]:
    init_db()
    session = SessionLocal()
    try:
        service = ProfileService(ProfileRepository(session))
        return service.list_profiles()
    finally:
        session.close()


def load_profile_detail(
    *,
    profile_id: int,
) -> tuple[Profile | None, Sequence[ResumeAsset], Sequence[WizardAnswer], Sequence[ProfileFact], Sequence[Run]]:
    init_db()
    session = SessionLocal()
    try:
        profile_service = ProfileService(ProfileRepository(session))
        resume_asset_service = ResumeAssetService(ResumeAssetRepository(session))
        wizard_answer_service = WizardAnswerService(WizardAnswerRepository(session))
        profile_fact_service = ProfileFactService(ProfileFactRepository(session))
        run_service = RunService(RunRepository(session))

        profile = profile_service.get_profile(profile_id=profile_id)
        if profile is None:
            return None, [], [], [], []

        return (
            profile,
            resume_asset_service.list_assets(profile_id=profile_id),
            wizard_answer_service.list_answers(profile_id=profile_id),
            profile_fact_service.list_facts(profile_id=profile_id),
            run_service.list_runs(profile_id=profile_id),
        )
    finally:
        session.close()


def create_draft_run(*, profile_id: int, mode: object) -> Run:
    init_db()
    session = SessionLocal()
    try:
        service = RunService(RunRepository(session))
        return service.create_draft_run(profile_id=profile_id, mode=mode)
    finally:
        session.close()


def format_profile_option(profile: Profile) -> str:
    return f"{profile.name} - {profile.target_title}"


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M")


def trim_text(text: str, *, limit: int = 240) -> str:
    normalized_text = text.strip()
    if len(normalized_text) <= limit:
        return normalized_text or "-"
    return normalized_text[: limit - 1].rstrip() + "..."


def render_profile_summary(profile: Profile) -> None:
    st.subheader("Profile")

    top_left, top_middle, top_right = st.columns(3)
    top_left.metric("Profile ID", profile.id)
    top_middle.metric("Status", "Active" if profile.is_active else "Inactive")
    top_right.metric("Updated", format_datetime(profile.updated_at))

    with st.container(border=True):
        st.markdown(f"**Name**: {profile.name}")
        st.markdown(f"**Target Title**: {profile.target_title}")
        st.markdown(
            f"**HH Resume URL**: {profile.hh_resume_url or 'Not provided'}"
        )
        st.caption(f"Created {format_datetime(profile.created_at)}")


def render_resume_assets(assets: Sequence[ResumeAsset]) -> None:
    st.subheader("Resume Assets")
    if not assets:
        st.info("No resume assets saved for this profile.")
        return

    for asset in assets:
        with st.container(border=True):
            left_column, right_column = st.columns([1, 3])
            with left_column:
                st.caption(f"Asset #{asset.id}")
                st.write(asset.source_type)
                st.caption(format_datetime(asset.created_at))
            with right_column:
                st.markdown(f"**File Path**: {asset.file_path or 'Not applicable'}")
                st.markdown(f"**Raw Text**: {trim_text(asset.raw_text)}")
                st.markdown(f"**Parsed Text**: {trim_text(asset.parsed_text)}")


def render_wizard_answers(answers: Sequence[WizardAnswer]) -> None:
    st.subheader("Wizard Answers")
    if not answers:
        st.info("No wizard answers saved for this profile.")
        return

    for answer in answers:
        with st.container(border=True):
            st.markdown(f"**{answer.question_text}**")
            st.caption(
                f"Key: {answer.question_key} | Saved {format_datetime(answer.created_at)}"
            )
            st.write(answer.answer_text)


def render_profile_facts(facts: Sequence[ProfileFact]) -> None:
    st.subheader("Generated Facts")
    if not facts:
        st.info("No generated facts found for this profile.")
        return

    for fact in facts:
        with st.container(border=True):
            st.markdown(f"**{fact.title}**")
            st.caption(
                f"Type: {fact.fact_type} | Generated {format_datetime(fact.created_at)}"
            )
            st.write(fact.content)


def render_runs(runs: Sequence[Run]) -> None:
    st.subheader("Runs")
    if not runs:
        st.info("No runs created for this profile yet.")
        return

    for run in runs:
        with st.container(border=True):
            left_column, right_column = st.columns([1, 3])
            with left_column:
                st.caption(f"Run #{run.id}")
                st.write(run.status)
            with right_column:
                st.markdown(f"**Mode**: {run.mode}")
                st.markdown(f"**Started**: {format_datetime(run.started_at)}")
                st.markdown(f"**Finished**: {format_datetime(run.finished_at)}")


def main() -> None:
    st.title("Profile Detail")
    st.caption("Review one profile together with its related resume assets, interview answers, and generated facts.")

    profiles = load_profiles()
    if not profiles:
        st.info("No profiles found. Create a profile first on the Profiles page.")
        return

    query_params = st.query_params
    requested_profile_id = int(query_params["profile_id"]) if "profile_id" in query_params else None

    default_index = 0
    if requested_profile_id is not None:
        for index, profile in enumerate(profiles):
            if profile.id == requested_profile_id:
                default_index = index
                break

    selected_profile = st.selectbox(
        "Choose a profile",
        options=profiles,
        index=default_index,
        format_func=format_profile_option,
    )
    st.query_params["profile_id"] = str(selected_profile.id)

    selected_mode = st.selectbox(
        "Run mode",
        options=list(SUPPORTED_RUN_MODES),
        index=0,
    )
    if st.button("Create Draft Run", type="primary", use_container_width=True):
        try:
            run = create_draft_run(profile_id=selected_profile.id, mode=selected_mode)
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["profile_detail_success_message"] = (
                f"Draft run #{run.id} created in {run.mode} mode."
            )
            st.rerun()

    success_message = st.session_state.pop("profile_detail_success_message", None)
    if success_message:
        st.success(success_message)

    profile, assets, answers, facts, runs = load_profile_detail(profile_id=selected_profile.id)
    if profile is None:
        st.error("The selected profile could not be loaded.")
        return

    count_one, count_two, count_three, count_four = st.columns(4)
    count_one.metric("Resume Assets", len(assets))
    count_two.metric("Wizard Answers", len(answers))
    count_three.metric("Generated Facts", len(facts))
    count_four.metric("Runs", len(runs))

    render_profile_summary(profile)
    st.divider()
    render_runs(runs)
    st.divider()
    render_resume_assets(assets)
    st.divider()
    render_wizard_answers(answers)
    st.divider()
    render_profile_facts(facts)


if __name__ == "__main__":
    main()
