from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.db.models.resume_asset import ResumeAsset
from app.repositories.resume_asset_repository import ResumeAssetRepository


class ResumeAssetService:
    def __init__(self, repository: ResumeAssetRepository) -> None:
        self.repository = repository
        self.settings = get_settings()

    def save_pasted_text(self, *, profile_id: int, raw_text: object) -> ResumeAsset:
        normalized_profile_id = self._validate_profile_id(profile_id)
        normalized_text = self._validate_required_text("raw_text", raw_text)
        return self.repository.create_resume_asset(
            profile_id=normalized_profile_id,
            source_type="pasted_text",
            file_path="",
            raw_text=normalized_text,
            parsed_text="",
        )

    def save_uploaded_file(
        self,
        *,
        profile_id: int,
        filename: object,
        file_bytes: bytes,
    ) -> ResumeAsset:
        normalized_profile_id = self._validate_profile_id(profile_id)
        normalized_filename = self._validate_required_text("filename", filename)
        if not file_bytes:
            raise ValueError("uploaded file is empty")

        destination = self._build_upload_path(
            profile_id=normalized_profile_id,
            filename=normalized_filename,
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file_bytes)

        return self.repository.create_resume_asset(
            profile_id=normalized_profile_id,
            source_type="uploaded_file",
            file_path=str(destination),
            raw_text=self._extract_raw_text(
                filename=normalized_filename,
                file_bytes=file_bytes,
            ),
            parsed_text="",
        )

    def get_latest_asset(self, *, profile_id: int) -> ResumeAsset | None:
        normalized_profile_id = self._validate_profile_id(profile_id)
        return self.repository.get_latest_by_profile(normalized_profile_id)

    def _build_upload_path(self, *, profile_id: int, filename: str) -> Path:
        safe_name = Path(filename).name or "resume_upload"
        upload_directory = self.settings.DATA_DIR / "resume_uploads" / f"profile_{profile_id}"
        unique_name = f"{uuid4().hex}_{safe_name}"
        return upload_directory / unique_name

    def _extract_raw_text(self, *, filename: str, file_bytes: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".txt":
            return file_bytes.decode("utf-8", errors="replace").strip()
        return ""

    def _validate_profile_id(self, profile_id: int) -> int:
        if profile_id <= 0:
            raise ValueError("profile_id must be positive")
        return profile_id

    def _validate_required_text(self, field_name: str, value: object) -> str:
        text = str(value).strip() if value is not None else ""
        if not text:
            raise ValueError(f"{field_name} is required")
        return text
