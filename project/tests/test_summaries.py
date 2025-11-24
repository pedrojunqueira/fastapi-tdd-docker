import json
import os

import pytest
from starlette.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from app.auth import get_current_user_from_azure
from app.config import Settings, get_settings
from app.main import create_application
from app.models.pydantic import CurrentUserSchema
from app.models.tortoise import User, UserRole


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


def create_mock_user_dependency(email: str, role: str):
    """Create a mock user dependency for testing."""

    async def _mock_user():
        role_enum = UserRole(role)
        oid = f"test-oid-{email}"
        user, _created = await User.get_or_create(
            azure_oid=oid, defaults={"email": email, "role": role_enum}
        )
        return CurrentUserSchema(id=user.id, email=user.email, role=user.role.value)

    return _mock_user


@pytest.fixture
def test_app_with_writer():
    """Test app with writer user."""
    from app.main import azure_scheme

    # Mock Azure config loading
    async def mock_load_config():
        pass

    azure_scheme.openid_config.load_config = mock_load_config

    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_current_user_from_azure] = create_mock_user_dependency(
        "writer@test.com", "writer"
    )
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_app_with_admin():
    """Test app with admin user."""
    from app.main import azure_scheme

    # Mock Azure config loading
    async def mock_load_config():
        pass

    azure_scheme.openid_config.load_config = mock_load_config

    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_current_user_from_azure] = create_mock_user_dependency(
        "admin@test.com", "admin"
    )
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_TEST_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as client:
        yield client


def test_create_summary(test_app_with_writer):
    response = test_app_with_writer.post(
        "/summaries/",
        data=json.dumps({"url": "https://foo.bar"}),
    )

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar/"


def test_create_summary_with_custom_summary(test_app_with_writer):
    """Test creating a summary with a custom summary provided"""
    response = test_app_with_writer.post(
        "/summaries/",
        data=json.dumps(
            {"url": "https://example.com/article", "summary": "Custom article summary"}
        ),
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["url"] == "https://example.com/article"
    assert response_data["summary"] == "Custom article summary"


def test_create_summaries_invalid_json(test_app_with_writer):
    response = test_app_with_writer.post("/summaries/", data=json.dumps({}))
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "url"]


def test_read_summary(test_app_with_writer):
    response = test_app_with_writer.post(
        "/summaries/",
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]

    response = test_app_with_writer.get(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar/"


def test_read_summary_incorrect_id(test_app_with_admin):
    response = test_app_with_admin.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(test_app_with_admin):
    response = test_app_with_admin.post(
        "/summaries/",
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]

    response = test_app_with_admin.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_writer):
    response = test_app_with_writer.post(
        "/summaries/",
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]

    response = test_app_with_writer.delete(f"/summaries/{summary_id}/")
    assert response.status_code == 200
    assert response.json()["url"] == "https://foo.bar/"


def test_remove_summary_incorrect_id(test_app_with_admin):
    response = test_app_with_admin.delete("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary(test_app_with_writer):
    response = test_app_with_writer.post(
        "/summaries/",
        data=json.dumps({"url": "https://foo.bar"}),
    )
    summary_id = response.json()["id"]

    response = test_app_with_writer.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({"url": "https://foo.bar", "summary": "updated!"}),
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar/"
    assert response_dict["summary"] == "updated!"


def test_update_summary_incorrect_id(test_app_with_writer):
    response = test_app_with_writer.put(
        "/summaries/999/",
        data=json.dumps({"url": "https://foo.bar/", "summary": "updated!"}),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"
