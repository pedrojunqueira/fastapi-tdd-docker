import json

import pytest

# Authentication helper
ADMIN_HEADERS = {"Authorization": "Bearer mock:admin@test.com:admin"}
WRITER_HEADERS = {"Authorization": "Bearer mock:writer@test.com:writer"}


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://foo.bar"}),
        headers=WRITER_HEADERS
    )

    assert response.status_code == 201
    assert response.json()["url"] == "https://foo.bar/"  # Pydantic normalizes URLs


def test_create_summary_without_summary_field(test_app_with_db):
    """Test creating a summary without providing the optional summary field"""
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://example.com"}),
        headers=WRITER_HEADERS
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["url"] == "https://example.com/"  # Pydantic normalizes URLs
    assert response_data["summary"] == "dummy summary"  # Default value


def test_create_summary_with_custom_summary(test_app_with_db):
    """Test creating a summary with a custom summary provided"""
    response = test_app_with_db.post(
        "/summaries/",
        data=json.dumps(
            {"url": "https://example.com/article", "summary": "Custom article summary"}
        ),
        headers=WRITER_HEADERS
    )

    assert response.status_code == 201
    response_data = response.json()
    assert (
        response_data["url"] == "https://example.com/article"
    )  # Original URL preserved
    assert response_data["summary"] == "Custom article summary"  # Custom value


def test_create_summaries_invalid_json(test_app):
    response = test_app.post("/summaries/", data=json.dumps({}), headers=WRITER_HEADERS)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    response = test_app.post("/summaries/", data=json.dumps({"url": "invalid://url"}))
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    )


def test_read_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://foo.bar"}),
        headers=WRITER_HEADERS
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/", headers=WRITER_HEADERS)
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar/"  # Pydantic normalizes URLs
    assert response_dict["summary"]
    assert response_dict["created_at"]


def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get("/summaries/999/", headers=ADMIN_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"

    response = test_app_with_db.get("/summaries/0/", headers=ADMIN_HEADERS)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"gt": 0},
                "input": "0",
                "loc": ["path", "id"],
                "msg": "Input should be greater than 0",
                "type": "greater_than",
            }
        ]
    }


def test_read_all_summaries(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://foo.bar"}),
        headers=ADMIN_HEADERS
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/", headers=ADMIN_HEADERS)
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://foo.bar"}),
        headers=WRITER_HEADERS
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.delete(f"/summaries/{summary_id}/", headers=WRITER_HEADERS)
    assert response.status_code == 200
    assert response.json() == {
        "id": summary_id,
        "url": "https://foo.bar/",
        "summary": "dummy summary",  # Default when not provided
    }  # Pydantic normalizes URLs


def test_remove_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.delete("/summaries/999/", headers=ADMIN_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", 
        data=json.dumps({"url": "https://foo.bar"}),
        headers=WRITER_HEADERS
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({"url": "https://foo.bar", "summary": "updated!"}),
        headers=WRITER_HEADERS
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar/"  # Pydantic normalizes URLs
    assert response_dict["summary"] == "updated!"
    assert response_dict["created_at"]


@pytest.mark.parametrize(
    ("summary_id", "payload", "status_code", "detail"),
    [
        (
            999,
            {"url": "https://foo.bar/", "summary": "updated!"},
            404,
            "Summary not found",
        ),
        (
            0,
            {"url": "https://foo.bar/", "summary": "updated!"},
            422,
            [
                {
                    "type": "greater_than",
                    "loc": ["path", "id"],
                    "msg": "Input should be greater than 0",
                    "input": "0",
                    "ctx": {"gt": 0},
                }
            ],
        ),
        (
            1,
            {},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "url"],
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ["body", "summary"],
                    "msg": "Field required",
                    "input": {},
                },
            ],
        ),
        (
            1,
            {"url": "https://foo.bar/"},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "summary"],
                    "msg": "Field required",
                    "input": {"url": "https://foo.bar/"},
                }
            ],
        ),
    ],
)
def test_update_summary_invalid(
    test_app_with_db, summary_id, payload, status_code, detail
):
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/", 
        data=json.dumps(payload),
        headers=ADMIN_HEADERS
    )
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    response = test_app.put(
        "/summaries/1/",
        data=json.dumps({"url": "invalid://url", "summary": "updated!"}),
        headers=ADMIN_HEADERS
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    )
