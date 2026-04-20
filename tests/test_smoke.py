from app.config import get_settings


def test_settings_defaults() -> None:
    settings = get_settings()
    assert settings.app_name == "CareerFlow AI"
    assert str(settings.database_path).endswith("careerflow.db")

