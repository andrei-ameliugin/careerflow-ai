from __future__ import annotations

from pathlib import Path

import pytest

from app.db.models.resume_asset import ResumeAsset
from app.services.resume_asset_service import ResumeAssetService


class FakeResumeAssetRepository:
    def __init__(self) -> None:
        self.created_assets: list[dict[str, object]] = []

    def create_resume_asset(self, **resume_asset_data: object) -> ResumeAsset:
        self.created_assets.append(resume_asset_data)
        return ResumeAsset(**resume_asset_data)

    def get_latest_by_profile(self, profile_id: int) -> ResumeAsset | None:
        if not self.created_assets:
            return None
        return ResumeAsset(**self.created_assets[-1])


def test_save_pasted_text_validates_required_text() -> None:
    service = ResumeAssetService(FakeResumeAssetRepository())

    with pytest.raises(ValueError, match="raw_text is required"):
        service.save_pasted_text(profile_id=1, raw_text="   ")


def test_save_pasted_text_creates_resume_asset() -> None:
    repository = FakeResumeAssetRepository()
    service = ResumeAssetService(repository)

    asset = service.save_pasted_text(profile_id=7, raw_text=" Senior backend engineer ")

    assert asset.profile_id == 7
    assert asset.source_type == "pasted_text"
    assert asset.raw_text == "Senior backend engineer"
    assert repository.created_assets[0]["file_path"] == ""


def test_save_uploaded_file_persists_text_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository = FakeResumeAssetRepository()
    service = ResumeAssetService(repository)
    monkeypatch.setattr(service.settings, "DATA_DIR", tmp_path)

    asset = service.save_uploaded_file(
        profile_id=3,
        filename="resume.txt",
        file_bytes=b"Python developer",
    )

    assert asset.source_type == "uploaded_file"
    assert asset.raw_text == "Python developer"
    assert Path(asset.file_path).exists()
    assert Path(asset.file_path).read_text(encoding="utf-8") == "Python developer"


def test_save_uploaded_file_keeps_binary_file_without_parsed_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = FakeResumeAssetRepository()
    service = ResumeAssetService(repository)
    monkeypatch.setattr(service.settings, "DATA_DIR", tmp_path)

    asset = service.save_uploaded_file(
        profile_id=3,
        filename="resume.pdf",
        file_bytes=b"%PDF-1.7",
    )

    assert asset.raw_text == ""
    assert Path(asset.file_path).exists()
