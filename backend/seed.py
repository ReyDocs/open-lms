import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.connection import engine, Base, AsyncSessionLocal
from app.infrastructure.database.models import (
    UserModel, CourseModel, ModuleModel, EnrollmentModel, AssignmentModel,
    SubmissionModel, AnnouncementModel, AnnouncementAttachmentModel,
    CalendarEventModel, FileResourceModel
)
from sqlalchemy import select


async def seed():
    print("Connecting to database and creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(UserModel).where(UserModel.email == "admin@openlms.edu"))
        if res.scalar_one_or_none():
            print("Database already contains seed data. Skipping seed.")
            return

        print("Seeding Users...")
        now = datetime.now(timezone.utc)

        # 1 Admin
        admin = UserModel(
            id=uuid4(),
            email="admin@openlms.edu",
            full_name="System Admin",
            role="admin",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin",
            created_at=now,
            updated_at=now,
        )
        session.add(admin)

        # 3 Teachers
        teachers_data = [
            ("Dr. Alan Turing", "alan.turing@openlms.edu"),
            ("Prof. Ada Lovelace", "ada.lovelace@openlms.edu"),
            ("Dr. Grace Hopper", "grace.hopper@openlms.edu"),
        ]
        teachers = []
        for name, email in teachers_data:
            t = UserModel(
                id=uuid4(),
                email=email,
                full_name=name,
                role="teacher",
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}",
                created_at=now,
                updated_at=now,
            )
            session.add(t)
            teachers.append(t)

        # 20 Students
        student_names = [
            "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Evan Wright",
            "Fiona Gallagher", "George Clark", "Hannah Abbott", "Ian Malcolm", "Julia Roberts",
            "Kevin Bacon", "Laura Croft", "Michael Scott", "Nora Valkyrie", "Oscar Martinez",
            "Pam Beesly", "Quentin Tarantino", "Rachel Green", "Steve Rogers", "Tony Stark"
        ]
        students = []
        for i, name in enumerate(student_names, 1):
            s = UserModel(
                id=uuid4(),
                email=f"{name.lower().replace(' ', '.')}@openlms.edu",
                full_name=name,
                role="student",
                student_id=f"STU{1000 + i}",
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}",
                created_at=now,
                updated_at=now,
            )
            session.add(s)
            students.append(s)

        await session.flush()
        print(f"Created 1 Admin, {len(teachers)} Teachers, {len(students)} Students.")

        # 5 Courses
        courses_data = [
            ("CS101", "Introduction to Computer Science", "Foundations of computation, algorithms, and Python programming.", "Fall 2026", teachers[0]),
            ("CS201", "Data Structures & Algorithms", "Advanced trees, graphs, sorting algorithms, and complexity analysis.", "Fall 2026", teachers[0]),
            ("MATH150", "Discrete Mathematics", "Logic, set theory, combinatorics, and graph theory for computing.", "Fall 2026", teachers[1]),
            ("ENG102", "Software Engineering Principles", "Clean architecture, testing, agile development, and system design.", "Fall 2026", teachers[1]),
            ("AI300", "Introduction to Artificial Intelligence", "Search algorithms, heuristic search, neural networks, and modern agents.", "Fall 2026", teachers[2]),
        ]

        courses = []
        for code, title, desc, sem, teacher in courses_data:
            c = CourseModel(
                id=uuid4(),
                code=code,
                title=title,
                description=desc,
                semester=sem,
                teacher_id=teacher.id,
                cover_image_url=f"https://picsum.photos/seed/{code}/800/400",
                created_at=now,
                updated_at=now,
            )
            session.add(c)
            courses.append(c)

        await session.flush()
        print(f"Created {len(courses)} Courses.")

        # Enroll students in courses (each student in 2-3 courses)
        for i, student in enumerate(students):
            assigned_courses = [courses[i % len(courses)], courses[(i + 1) % len(courses)], courses[(i + 2) % len(courses)]]
            for c in assigned_courses:
                enrollment = EnrollmentModel(
                    id=uuid4(),
                    user_id=student.id,
                    course_id=c.id,
                    method="pool",
                    enrolled_at=now,
                )
                session.add(enrollment)

        await session.flush()
        print("Enrolled students in courses.")

        # Modules and Assignments for each course
        all_assignments = []
        assignment_counter = 1

        for c_idx, course in enumerate(courses):
            # 3 to 4 modules per course
            module_titles = [
                f"Week 1: Fundamentals of {course.title}",
                f"Week 2: Deep Dive into Core Concepts",
                f"Week 3: Practical Applications & Labs",
                f"Week 4: Final Project & Review",
            ]

            course_modules = []
            for m_order, m_title in enumerate(module_titles):
                m = ModuleModel(
                    id=uuid4(),
                    title=m_title,
                    description=f"Overview and materials for {m_title}",
                    sort_order=m_order,
                    course_id=course.id,
                    created_at=now,
                )
                session.add(m)
                course_modules.append(m)

            await session.flush()

            # Add file resources to module 0
            res = FileResourceModel(
                id=uuid4(),
                module_id=course_modules[0].id,
                uploaded_by=course.teacher_id,
                file_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                file_name="Syllabus_and_Schedule.pdf",
                file_type="pdf",
                file_size=14520,
                uploaded_at=now,
            )
            session.add(res)

            # 3 to 4 assignments per course (Total 18+ assignments across 5 courses)
            for a_idx in range(3):
                is_published = not (c_idx == 4 and a_idx == 2)  # leave one as draft
                due_offset = (a_idx + 1) * 4  # due in 4, 8, 12 days
                due_date = now + timedelta(days=due_offset)

                assign = AssignmentModel(
                    id=uuid4(),
                    title=f"Assignment {assignment_counter}: {course.code} Problem Set {a_idx + 1}",
                    description=f"<p>Complete the exercise sheet for <strong>{course_modules[a_idx].title}</strong>. Submit your solutions as a PDF or ZIP file.</p>",
                    total_points=100,
                    status="published" if is_published else "draft",
                    due_date=due_date,
                    module_id=course_modules[a_idx].id,
                    course_id=course.id,
                    created_at=now,
                    updated_at=now,
                )
                session.add(assign)
                all_assignments.append(assign)
                assignment_counter += 1

                # Auto calendar event if published
                if is_published:
                    cal = CalendarEventModel(
                        id=uuid4(),
                        course_id=course.id,
                        created_by=course.teacher_id,
                        title=f"Due: {assign.title}",
                        description=f"Assignment due date",
                        event_datetime=due_date,
                        source="auto",
                        assignment_id=assign.id,
                        created_at=now,
                    )
                    session.add(cal)

            # Manual calendar event (e.g. Office Hours)
            manual_cal = CalendarEventModel(
                id=uuid4(),
                course_id=course.id,
                created_by=course.teacher_id,
                title=f"{course.code} Weekly Office Hours",
                description="Drop in via Zoom or Hall 401 for questions and project help.",
                event_datetime=now + timedelta(days=2, hours=4),
                source="manual",
                created_at=now,
            )
            session.add(manual_cal)

            # Course Announcement with attachment
            ann = AnnouncementModel(
                id=uuid4(),
                course_id=course.id,
                author_id=course.teacher_id,
                title=f"Welcome to {course.code}: {course.title}!",
                content=f"<p>Welcome everyone! Please review the syllabus in <strong>Week 1</strong> and make sure you have the required textbooks and development tools installed.</p>",
                created_at=now - timedelta(days=1),
            )
            session.add(ann)

            att = AnnouncementAttachmentModel(
                id=uuid4(),
                announcement_id=ann.id,
                file_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                file_name="Course_Guidelines.pdf",
                file_size=20480,
            )
            session.add(att)

        await session.flush()
        print(f"Created {len(all_assignments)} Assignments and course announcements.")

        # Submissions and Grades for published assignments
        print("Creating sample submissions and grades...")
        for assign in all_assignments:
            if assign.status != "published":
                continue

            # Find enrolled students for this course
            enrolled_stmt = select(EnrollmentModel.user_id).where(EnrollmentModel.course_id == assign.course_id)
            student_ids = (await session.execute(enrolled_stmt)).scalars().all()

            for s_id in student_ids[:4]:  # First 4 students submit
                sub = SubmissionModel(
                    id=uuid4(),
                    assignment_id=assign.id,
                    student_id=s_id,
                    file_url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    file_name="Solution_Submission.pdf",
                    file_size=51200,
                    submitted_at=now - timedelta(hours=5),
                    grade=92,
                    feedback="Great work! Comprehensive test coverage and clear algorithmic steps.",
                    graded_at=now - timedelta(hours=1),
                )
                session.add(sub)

        await session.commit()
        print("✅ Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
