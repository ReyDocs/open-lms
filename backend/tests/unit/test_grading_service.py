import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.application.services.grading_service import GradingService
from app.application.dtos.grading_dtos import GradeSubmissionDTO
from app.domain.entities.user import User
from app.domain.entities.submission import Submission
from app.domain.entities.assignment import Assignment


@pytest.mark.asyncio
async def test_grade_submission_valid():
    submission_repo = AsyncMock()
    assignment_repo = AsyncMock()
    course_repo = AsyncMock()
    enrollment_repo = AsyncMock()
    user_repo = AsyncMock()
    notif_service = AsyncMock()

    service = GradingService(
        submission_repo, assignment_repo, course_repo, enrollment_repo, user_repo, notif_service
    )

    teacher = User(id=uuid4(), email="prof@edu.com", full_name="Prof X", role="teacher")
    student = User(id=uuid4(), email="stu@edu.com", full_name="Stu Dent", role="student")

    assign_id = uuid4()
    sub_id = uuid4()
    now = datetime.now(timezone.utc)

    assignment = Assignment(
        id=assign_id,
        title="Midterm",
        description="Exam",
        total_points=100,
        status="published",
        due_date=now,
        module_id=uuid4(),
        course_id=uuid4(),
    )
    submission = Submission(
        id=sub_id,
        assignment_id=assign_id,
        student_id=student.id,
        file_url="/file.pdf",
        file_name="sub.pdf",
        file_size=1024,
        submitted_at=now,
    )

    submission_repo.get_by_id.return_value = submission
    assignment_repo.get_by_id.return_value = assignment
    user_repo.get_by_id.return_value = student
    submission_repo.update.side_effect = lambda s: s

    dto = GradeSubmissionDTO(submission_id=sub_id, grade=95, feedback="Well done!")
    res = await service.grade_submission(dto, teacher)

    assert res.grade == 95
    assert res.feedback == "Well done!"
    notif_service.create_notification.assert_called_once()


@pytest.mark.asyncio
async def test_grade_submission_out_of_bounds():
    submission_repo = AsyncMock()
    assignment_repo = AsyncMock()
    course_repo = AsyncMock()
    enrollment_repo = AsyncMock()
    user_repo = AsyncMock()

    service = GradingService(
        submission_repo, assignment_repo, course_repo, enrollment_repo, user_repo
    )

    teacher = User(id=uuid4(), email="prof@edu.com", full_name="Prof X", role="teacher")
    sub_id = uuid4()
    now = datetime.now(timezone.utc)

    assignment = Assignment(
        id=uuid4(),
        title="Midterm",
        description="Exam",
        total_points=50,
        status="published",
        due_date=now,
        module_id=uuid4(),
        course_id=uuid4(),
    )
    submission = Submission(
        id=sub_id,
        assignment_id=assignment.id,
        student_id=uuid4(),
        file_url="/file.pdf",
        file_name="sub.pdf",
        file_size=1024,
        submitted_at=now,
    )

    submission_repo.get_by_id.return_value = submission
    assignment_repo.get_by_id.return_value = assignment

    # Grade is 60 which is > total_points 50
    dto = GradeSubmissionDTO(submission_id=sub_id, grade=60)
    with pytest.raises(ValueError):
        await service.grade_submission(dto, teacher)
