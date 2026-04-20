from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import streamlit as st

from app.db import SessionLocal, init_db
from app.db.models.profile import Profile
from app.repositories import ProfileRepository
from app.services import ProfileService


def create_profile(*, name: object, target_title: object, hh_resume_url: object) -> Profile:
    init_db()
    session = SessionLocal()
    try:
        service = ProfileService(ProfileRepository(session))
        return service.create_profile(
            name=name,
            target_title=target_title,
            hh_resume_url=hh_resume_url,
        )
    finally:
        session.close()


def load_profiles() -> Sequence[Profile]:
    init_db()
    session = SessionLocal()
    try:
        service = ProfileService(ProfileRepository(session))
        return service.list_profiles()
    finally:
        session.close()


def serialize_profiles(profiles: Sequence[Profile]) -> list[dict[str, Any]]:
    return [
        {
            "ID": profile.id,
            "Name": profile.name,
            "Target Title": profile.target_title,
            "HH Resume URL": profile.hh_resume_url,
            "Active": profile.is_active,
            "Created At": profile.created_at,
            "Updated At": profile.updated_at,
        }
        for profile in profiles
    ]


def main() -> None:
    st.title("Profiles")

    with st.form("create_profile_form", clear_on_submit=True):
        name = st.text_input("Name")
        target_title = st.text_input("Target Title")
        hh_resume_url = st.text_input("HH Resume URL")
        submitted = st.form_submit_button("Create Profile")

    if submitted:
        try:
            profile = create_profile(
                name=name,
                target_title=target_title,
                hh_resume_url=hh_resume_url,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["profiles_success_message"] = (
                f"Profile created: {profile.name}"
            )
            st.rerun()

    success_message = st.session_state.pop("profiles_success_message", None)
    if success_message:
        st.success(success_message)

    profiles = load_profiles()
    if not profiles:
        st.info("No profiles found.")
        return

    st.dataframe(
        serialize_profiles(profiles),
        hide_index=True,
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
