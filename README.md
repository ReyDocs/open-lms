# OpenLMS — MVP (Phase 1)

OpenLMS is a lightweight, clean architecture Learning Management System designed for higher education institutions.

## Architecture

The project strictly follows **Clean Architecture** (Robert C. Martin) with unidirectional inward dependencies:
- **Domain Layer (`backend/app/domain`)**: Pure business entities (`User`, `Course`, `Module`, `Assignment`, `Submission`, `Announcement`, `Notification`, `CalendarEvent`, `Enrollment`) and value objects (`EmailAddress`, `FileType`, `PointScore`). Zero framework dependencies.
- **Application Layer (`backend/app/application`)**: Abstract repository and service interfaces (`IUserRepository`, etc.), DTOs, and Use Case services (`CourseService`, `AssignmentService`, `GraduationService`, etc.).
- **Infrastructure Layer (`backend/app/infrastructure`)**: Concrete adapters for SQLAlchemy, database models, Supabase Storage, Resend Email, Google OAuth, and JWT authentication.
- **Presentation Layer (`backend/app/presentation`)**: FastAPI route handlers, Pydantic schemas, dependency injection, and standardized error middleware.

The frontend is built with React 18+, Vite, TypeScript, Tailwind CSS, TanStack Query, and React Router v6.

---

## Features Implemented (100% Phase 1 MVP Scope)

1. **Authentication & Security:**
   - Google OAuth 2.0 flow
   - JWT pair: 15-minute access token, 7-day refresh token rotated on use
   - Instant Demo/Evaluation mode (switch between Admin, Teacher, and Student)
   - Role-Based Access Control (Admin, Teacher, Student)
2. **Admin Panel:**
   - User Management (CRUD, filter by role, search)
   - Student Pool Bulk Import (CSV upload with name, email, student_id)
   - System Settings (app name, support email, maintenance mode toggle)
   - Institutional Course Oversight (view all courses)
3. **Course & Module Management:**
   - Teacher course creation, editing, deletion
   - Course-level search by name or course code
   - Sequential modules with sort order and file resource attachments (lecture slides, reading PDFs)
4. **Student Enrollment Pathways:**
   - **Pathway A (Admin-Imported Pool):** Teacher selects pre-registered students from the pool to add directly to a course.
   - **Pathway B (Email Invite):** Teacher enters student's email to send an invite email via Resend; student is auto-enrolled on login.
5. **Assignments & Submissions:**
   - Points-based assignment lifecycle (draft and published states)
   - Automated calendar event creation upon publishing
   - File upload submissions (PDF, DOCX, ZIP, etc. with 25MB limit)
   - Student resubmissions allowed before the due date; closed after the deadline
6. **Grading & Gradebook:**
   - Points-based submission grading with feedback
   - Full gradebook table (students × assignments) with total points and overall percentage
   - CSV gradebook export for teachers
   - Student view of own grades and teacher feedback
7. **Course Announcements:**
   - Course-level announcements with rich text HTML (sanitized with Bleach)
   - File attachments
   - Instant in-app and email notifications dispatched to all enrolled students
8. **Academic Calendar:**
   - Aggregated calendar across all user's courses
   - Automated assignment due dates
   - Teacher manual events (office hours, review sessions)
9. **Notifications:**
   - In-app notification center with unread count badge
   - Triggers for new announcements, published assignments, graded submissions, and invitations
   - Mark as read / mark all as read
10. **Database Seeding (`seed.py`):**
    - 1 Admin, 3 Teachers, 20 Students
    - 5 Courses with 3–4 modules each
    - 15+ Assignments (mix of published and draft)
    - Sample student submissions, grades, announcements, attachments, and calendar events

---

## Getting Started

### 1. Backend Setup

```bash
cd backend

# Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Seed database with sample data
python3 seed.py

# Run tests
pytest

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

Visit `http://localhost:5173` to access the application.
