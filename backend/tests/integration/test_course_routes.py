import pytest


@pytest.mark.asyncio
async def test_create_and_list_course(client, sample_teacher, auth_headers):
    headers = auth_headers(sample_teacher)

    create_resp = await client.post(
        "/api/v1/courses",
        headers=headers,
        json={
            "title": "Algorithms 101",
            "code": "CS101",
            "description": "Fundamental algorithms course.",
            "semester": "Fall 2026",
        },
    )
    assert create_resp.status_code == 200
    course = create_resp.json()
    assert course["code"] == "CS101"
    course_id = course["id"]

    # List courses
    list_resp = await client.get("/api/v1/courses", headers=headers)
    assert list_resp.status_code == 200
    courses_data = list_resp.json()
    assert any(c["id"] == course_id for c in courses_data["data"])


@pytest.mark.asyncio
async def test_student_cannot_create_course(client, sample_student, auth_headers):
    headers = auth_headers(sample_student)
    create_resp = await client.post(
        "/api/v1/courses",
        headers=headers,
        json={
            "title": "Unauthorized Course",
            "code": "HACK101",
            "description": "Should fail",
            "semester": "Fall 2026",
        },
    )
    assert create_resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_cannot_create_course(client, sample_admin, auth_headers):
    headers = auth_headers(sample_admin)
    create_resp = await client.post(
        "/api/v1/courses",
        headers=headers,
        json={
            "title": "Admin Course",
            "code": "ADM101",
            "description": "Admins cannot create courses per PRD",
            "semester": "Fall 2026",
        },
    )
    assert create_resp.status_code == 403

    # Admin listing user courses returns empty list (all courses are accessed via /admin/courses)
    list_resp = await client.get("/api/v1/courses", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["data"] == []
