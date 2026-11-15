# OpenLMS — Product Requirements Document (PRD)

> **Version:** 1.0 — MVP (Phase 1)
> **Date:** 2026-11-14
> **Status:** Approved for Development
> **License:** Apache 2.0

---

## Table of Contents

1. [Overview](#1-overview)
2. [Goals & Constraints](#2-goals--constraints)
3. [User Roles & Permissions](#3-user-roles--permissions)
4. [MVP Feature Specifications](#4-mvp-feature-specifications)
5. [Clean Code Architecture](#5-clean-code-architecture)
6. [Backend Architecture](#6-backend-architecture)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Database Schema](#8-database-schema)
9. [API Design](#9-api-design)
10. [Authentication & Security](#10-authentication--security)
11. [Infrastructure & Deployment](#11-infrastructure--deployment)
12. [Phased Roadmap](#12-phased-roadmap)
13. [Development Standards](#13-development-standards)
14. [Appendix](#14-appendix)

---

## 1. Overview

### 1.1 Product Summary

**OpenLMS** is a custom, small-scale Learning Management System designed for **higher education** institutions. It draws inspiration from Google Classroom's simplicity and Moodle's structural depth, targeting a single institution with **500+ users**.

### 1.2 Core Value Proposition

A lightweight, open-source LMS that gives teachers full control over course management, student enrollment, and grading — without the bloat of enterprise platforms.

### 1.3 Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | React 18+ · Vite · Shadcn/ui · Tailwind CSS · React Router v6 · TanStack Query |
| Backend | FastAPI · Python 3.11+ · SQLAlchemy · Alembic |
| Database | Supabase PostgreSQL |
| File Storage | Supabase Storage |
| Authentication | Google OAuth 2.0 · JWT |
| Email | Resend |
| Deployment | Netlify (frontend) · Render (backend) |
| Repository | Monorepo |

---

## 2. Goals & Constraints

### 2.1 MVP Goals

- Deliver a **functional LMS** with course management, assignments, grading, and notifications
- Support **daily client demos** — the system must be presentable at every increment
- Maintain **clean architecture** boundaries to support iterative expansion across phases

### 2.2 Constraints

| Constraint | Detail |
|---|---|
| Scale | Single institution, 500+ concurrent users |
| Platform | Web-only (responsive, mobile-browser compatible) |
| Auth | Google OAuth only — all users must have Google accounts |
| Language | English only |
| Budget | PaaS free/starter tiers initially |
| Real-time | None in MVP — polling/fetch-on-load only |

### 2.3 Success Metrics

$$
\text{MVP Completeness} = \frac{\text{Implemented Features}}{\text{Total MVP Features}} \times 100\%
$$

Target: **100%** of Phase 1 features before Phase 2 begins.

---

## 3. User Roles & Permissions

### 3.1 Role Definitions

| Role | Description |
|---|---|
| **Admin** | System administrator. Manages users, views all courses, configures system settings. |
| **Teacher** | Creates and manages courses, modules, assignments, announcements. Enrolls students. Grades submissions. |
| **Student** | Enrolls in courses (via teacher), views content, submits assignments, views grades. |

### 3.2 Permission Matrix

| Action | Admin | Teacher | Student |
|---|:---:|:---:|:---:|
| Manage users (CRUD, bulk import) | ✅ | ❌ | ❌ |
| View all courses | ✅ | ❌ | ❌ |
| System settings | ✅ | ❌ | ❌ |
| Create / edit / delete courses | ❌ | ✅ | ❌ |
| Create / manage modules | ❌ | ✅ | ❌ |
| Enroll students (from pool or invite) | ❌ | ✅ | ❌ |
| Create / publish assignments | ❌ | ✅ | ❌ |
| Grade submissions | ❌ | ✅ | ❌ |
| Post announcements | ❌ | ✅ | ❌ |
| Upload course files | ❌ | ✅ | ❌ |
| Add calendar events | ❌ | ✅ | ❌ |
| Export gradebook (CSV) | ❌ | ✅ | ❌ |
| View courses & modules | ❌ | ✅ | ✅ |
| Download files | ❌ | ✅ | ✅ |
| Submit / resubmit assignments | ❌ | ❌ | ✅ |
| View own grades | ❌ | ❌ | ✅ |
| View announcements | ❌ | ✅ | ✅ |
| View calendar | ❌ | ✅ | ✅ |
| Search courses | ✅ | ✅ | ✅ |
| Receive notifications | ✅ | ✅ | ✅ |

---

## 4. MVP Feature Specifications

### 4.1 Authentication

- **Google OAuth 2.0** is the sole authentication method
- On successful OAuth, the backend issues a **JWT pair**:
  - Access token: **15-minute** expiry
  - Refresh token: **7-day** expiry, **rotated on use**
- New users are auto-created on first login (profile populated from Google: name, email, avatar)
- Default role for new users: **Student** (Admin promotes to Teacher via user management)

$$
T_{\text{access}} = 15 \text{ min}, \quad T_{\text{refresh}} = 7 \text{ days}
$$

### 4.2 Enrollment

Two enrollment pathways:

**Pathway A — Admin-Imported Pool:**
1. Admin bulk-imports students (CSV upload: name, email, student ID)
2. Users are pre-registered in the system (no account yet, just records)
3. Teacher searches the pool and adds students to a course
4. Student logs in via Google OAuth → matched by email → sees enrolled courses

**Pathway B — Teacher Email Invite:**
1. Teacher enters student's email address
2. System sends an invitation email via Resend
3. Student clicks link → redirected to Google OAuth login → auto-enrolled on success
4. If user doesn't exist in system, account is created from Google profile data

### 4.3 Course & Module Management

**Course:**
- Fields: title, code (e.g., `CS101`), description, semester/term, cover image (optional)
- Teacher creates courses; students see only courses they're enrolled in
- Admin can view all courses

**Modules (within a course):**
- Ordered containers (e.g., "Week 1: Introduction", "Week 2: Variables")
- Each module holds **assignments** and **file resources**
- Modules can be reordered via drag-and-drop (nice-to-have) or manual ordering
- **Announcements are course-level**, not inside modules

### 4.4 Assignments

**Lifecycle:**

```mermaid
stateDiagram-v2
    [*] --> Draft : Teacher creates
    Draft --> Published : Teacher publishes
    Published --> Submitted : Student uploads file
    Submitted --> Resubmitted : Student uploads new file (before due date)
    Submitted --> Graded : Teacher assigns points
    Resubmitted --> Graded : Teacher assigns points
    Graded --> [*]
```

**Assignment Fields:**
| Field | Type | Required |
|---|---|:---:|
| Title | string | ✅ |
| Description | rich text | ✅ |
| Due date | datetime | ✅ |
| Total points | integer | ✅ |
| Status | enum: `draft`, `published` | ✅ |
| Module | foreign key | ✅ |
| Attachments | files | ❌ |

**Submission Rules:**
- **File upload only** (MVP)
- Accepted types: PDF, DOCX, PPTX, XLSX, JPG, PNG, ZIP, MP4, MP3, CSV, TXT
- Max file size: **25 MB**
- Students may **resubmit at any time before the due date** — latest submission is graded
- After due date, submissions are closed (no late submissions in MVP)

### 4.5 Grading

**Model:** Points-based

$$
\text{Grade}_i = \frac{p_i}{P_i} \quad \text{where } p_i = \text{points earned}, \; P_i = \text{total points}
$$

**Gradebook:**
- Table view: rows = students, columns = assignments, cells = $p_i / P_i$
- Visible to teachers (all students) and students (own grades only)
- **CSV export** for teachers (downloads full gradebook as `.csv`)
- Grades are entered when a teacher grades a submission (not directly in the gradebook)

### 4.6 Announcements

- **Course-level** (not inside modules)
- Content: **Rich text** (Tiptap editor) + **file attachments**
- Ordered by newest first
- Creating an announcement triggers a notification to all enrolled students

### 4.7 Calendar

- **Auto-populated:** Assignment due dates appear automatically
- **Manual events:** Teachers can add custom events (title, description, datetime) — e.g., "Office Hours", "Review Session"
- Calendar view per course + aggregated view on dashboard
- No scheduling / room assignment functionality

### 4.8 Notifications

**Triggers:**

| Event | Recipients | Channels |
|---|---|---|
| New announcement posted | All enrolled students | In-app + Email |
| New assignment published | All enrolled students | In-app + Email |
| Assignment graded | Submitting student | In-app + Email |
| Enrollment (added to course) | Student | In-app + Email |
| Assignment due date reminder | All enrolled students | In-app + Email |

**In-App:** Bell icon in header → notification panel (unread count badge)

**Email:** Sent via **Resend** — HTML email templates using React Email

### 4.9 Admin Panel

- **User Management:** CRUD operations, bulk import via CSV, role assignment
- **Course Visibility:** View all courses (read-only oversight)
- **System Settings:** App name, logo, support email, maintenance mode

### 4.10 Dashboard

All users see a unified dashboard after login:
- **Course cards** — enrolled (students) or taught (teachers) courses
- **Upcoming deadlines** — next 7 days of assignment due dates
- **Recent announcements** — latest announcements across all courses

### 4.11 Search

- **Basic course search** by course name or course code
- Available to all authenticated users
- Debounced search input in the sidebar

---

## 5. Clean Code Architecture

> [!IMPORTANT]
> OpenLMS follows **Clean Architecture** (Robert C. Martin) to enforce separation of concerns, testability, and independence from frameworks. The dependency rule is absolute: **inner layers never depend on outer layers.**

### 5.1 The Dependency Rule

$$
\text{Dependencies} : \text{Frameworks} \rightarrow \text{Adapters} \rightarrow \text{Use Cases} \rightarrow \text{Entities}
$$

All source code dependencies point **inward**. The inner layers define interfaces (ports); the outer layers provide implementations (adapters).

```mermaid
flowchart TD
    subgraph E["🟢 Entities (Domain Layer)"]
        E1["Business Objects"]
        E2["Domain Rules"]
        E3["Value Objects"]
    end

    subgraph U["🔵 Use Cases (Application Layer)"]
        U1["Application Services"]
        U2["Port Interfaces"]
        U3["DTOs"]
    end

    subgraph A["🟠 Adapters (Infrastructure Layer)"]
        A1["Repository Implementations"]
        A2["External Service Clients"]
        A3["Security Implementations"]
    end

    subgraph F["🔴 Frameworks (Presentation Layer)"]
        F1["FastAPI Routes"]
        F2["React Components"]
        F3["Database Drivers"]
    end

    F --> A --> U --> E
```

### 5.2 Layer Responsibilities

**Layer 1 — Entities (Domain):**
> Pure business objects with zero framework dependencies. A `Course` entity knows what a course *is*, not how it's stored or displayed.

- Domain models (User, Course, Module, Assignment, Submission, etc.)
- Business rules and validation logic
- Value objects (e.g., `EmailAddress`, `FileType`, `PointScore`)
- No imports from SQLAlchemy, FastAPI, or any external library

**Layer 2 — Use Cases (Application):**
> Orchestrate business logic by coordinating entities and calling port interfaces. Each use case represents one user action.

- Application services (e.g., `CreateCourseUseCase`, `SubmitAssignmentUseCase`, `GradeSubmissionUseCase`)
- Port interfaces (abstract repository contracts, e.g., `ICourseRepository`, `INotificationService`)
- Input/Output DTOs for each use case
- No knowledge of HTTP, databases, or UI

**Layer 3 — Adapters (Infrastructure):**
> Implement the port interfaces defined by the use case layer. This is where SQLAlchemy, Supabase, Resend, and Google OAuth live.

- Repository implementations (e.g., `SQLAlchemyCourseRepository` implements `ICourseRepository`)
- External service clients (Resend email, Supabase Storage, Google OAuth)
- Security implementations (JWT encoding/decoding, password hashing if ever needed)
- Data mappers (ORM model ↔ domain entity conversion)

**Layer 4 — Frameworks (Presentation):**
> The outermost layer. FastAPI routes, React components, database drivers. These are interchangeable without touching business logic.

- FastAPI route handlers (controllers)
- Request/response serialization (Pydantic models for API)
- Dependency injection wiring (`Depends()`)
- React pages, components, hooks

### 5.3 Key Principles

| Principle | Application in OpenLMS |
|---|---|
| **Single Responsibility** | Each module/class has one reason to change. A repository handles data access, not business rules. |
| **Dependency Inversion** | Use cases depend on abstract `IRepository` interfaces, not concrete SQLAlchemy implementations. |
| **Interface Segregation** | Repositories expose only the methods their consumers need — no god-repositories. |
| **Open/Closed** | New features (e.g., quizzes in Phase 2) add new use cases and entities without modifying existing ones. |
| **Don't Repeat Yourself** | Shared validation logic lives in domain entities, not duplicated across routes and services. |

### 5.4 Dependency Injection Flow (FastAPI)

```mermaid
flowchart LR
    Route["Route Handler"] -->|Depends| UC["Use Case Service"]
    UC -->|Depends| Repo["Repository Interface"]
    Repo -.->|Implemented by| SQLRepo["SQLAlchemy Repository"]
    UC -->|Depends| Notif["INotificationService"]
    Notif -.->|Implemented by| ResendSvc["Resend Email Service"]
    Route -->|Depends| Auth["Auth Dependency"]
    Auth -->|validates| JWT["JWT Token"]
```

```python
# Example: Dependency Injection in FastAPI
# presentation/api/v1/courses.py

@router.post("/", response_model=CourseResponse)
async def create_course(
    data: CreateCourseRequest,
    current_user: User = Depends(require_teacher),  # Auth guard
    course_service: CourseService = Depends(get_course_service),  # Use case
):
    return await course_service.create_course(data, current_user)
```

---

## 6. Backend Architecture

### 6.1 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app factory
│   ├── config.py                        # Settings via pydantic-settings
│   │
│   ├── domain/                          # 🟢 Layer 1: Entities
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── user.py                  # User entity
│   │   │   ├── course.py                # Course entity
│   │   │   ├── module.py                # Module entity
│   │   │   ├── assignment.py            # Assignment entity
│   │   │   ├── submission.py            # Submission entity
│   │   │   ├── announcement.py          # Announcement entity
│   │   │   ├── notification.py          # Notification entity
│   │   │   └── calendar_event.py        # CalendarEvent entity
│   │   └── value_objects/
│   │       ├── email_address.py
│   │       ├── file_type.py
│   │       └── point_score.py
│   │
│   ├── application/                     # 🔵 Layer 2: Use Cases
│   │   ├── __init__.py
│   │   ├── interfaces/                  # Port interfaces (ABCs)
│   │   │   ├── repositories/
│   │   │   │   ├── i_user_repository.py
│   │   │   │   ├── i_course_repository.py
│   │   │   │   ├── i_assignment_repository.py
│   │   │   │   ├── i_submission_repository.py
│   │   │   │   ├── i_announcement_repository.py
│   │   │   │   ├── i_notification_repository.py
│   │   │   │   └── i_calendar_event_repository.py
│   │   │   └── services/
│   │   │       ├── i_email_service.py
│   │   │       ├── i_storage_service.py
│   │   │       └── i_auth_service.py
│   │   ├── services/                    # Application services (use cases)
│   │   │   ├── user_service.py
│   │   │   ├── course_service.py
│   │   │   ├── module_service.py
│   │   │   ├── assignment_service.py
│   │   │   ├── submission_service.py
│   │   │   ├── announcement_service.py
│   │   │   ├── grading_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── calendar_service.py
│   │   │   └── enrollment_service.py
│   │   └── dtos/                        # Input/Output DTOs
│   │       ├── user_dtos.py
│   │       ├── course_dtos.py
│   │       ├── assignment_dtos.py
│   │       └── ...
│   │
│   ├── infrastructure/                  # 🟠 Layer 3: Adapters
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── connection.py            # SQLAlchemy engine & session
│   │   │   ├── models/                  # ORM models (SQLAlchemy)
│   │   │   │   ├── user_model.py
│   │   │   │   ├── course_model.py
│   │   │   │   ├── module_model.py
│   │   │   │   ├── assignment_model.py
│   │   │   │   ├── submission_model.py
│   │   │   │   ├── announcement_model.py
│   │   │   │   ├── notification_model.py
│   │   │   │   └── calendar_event_model.py
│   │   │   └── migrations/              # Alembic migrations
│   │   │       ├── env.py
│   │   │       └── versions/
│   │   ├── repositories/                # Concrete repository implementations
│   │   │   ├── sqlalchemy_user_repo.py
│   │   │   ├── sqlalchemy_course_repo.py
│   │   │   ├── sqlalchemy_assignment_repo.py
│   │   │   └── ...
│   │   ├── external/                    # External service adapters
│   │   │   ├── resend_email_service.py
│   │   │   ├── supabase_storage_service.py
│   │   │   └── google_oauth_service.py
│   │   └── security/
│   │       └── jwt_handler.py           # JWT encode/decode/refresh
│   │
│   └── presentation/                    # 🔴 Layer 4: Frameworks
│       ├── __init__.py
│       ├── api/
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py            # Aggregates all v1 routers
│       │       ├── auth_routes.py
│       │       ├── user_routes.py
│       │       ├── course_routes.py
│       │       ├── module_routes.py
│       │       ├── assignment_routes.py
│       │       ├── submission_routes.py
│       │       ├── announcement_routes.py
│       │       ├── grading_routes.py
│       │       ├── notification_routes.py
│       │       ├── calendar_routes.py
│       │       └── admin_routes.py
│       ├── dependencies/
│       │   ├── auth.py                  # require_admin, require_teacher, require_student
│       │   └── services.py             # DI factories (get_course_service, etc.)
│       ├── middleware/
│       │   ├── cors.py
│       │   └── error_handler.py
│       └── schemas/                     # Pydantic request/response models
│           ├── auth_schemas.py
│           ├── user_schemas.py
│           ├── course_schemas.py
│           ├── assignment_schemas.py
│           └── ...
│
├── tests/
│   ├── conftest.py                      # Fixtures, test DB setup
│   ├── unit/
│   │   ├── test_user_service.py
│   │   ├── test_course_service.py
│   │   ├── test_assignment_service.py
│   │   └── ...
│   └── integration/
│       ├── test_auth_routes.py
│       ├── test_course_routes.py
│       └── ...
│
├── seed.py                              # Database seeding script
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── .env.example
```

### 6.2 Key Backend Patterns

| Pattern | Implementation |
|---|---|
| **Dependency Injection** | FastAPI `Depends()` chain: Route → Auth → Service → Repository |
| **Repository Pattern** | Abstract `IRepository` in application layer; SQLAlchemy implementation in infrastructure |
| **Service Layer** | One service per aggregate (CourseService, AssignmentService, etc.) |
| **DTO Pattern** | Separate Pydantic schemas for API (presentation) and DTOs for internal use case communication |
| **Factory Pattern** | App factory in `main.py` for configurable startup |

---

## 7. Frontend Architecture

### 7.1 Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx                      # Root component, providers, router
│   │   ├── routes.tsx                   # React Router v6 route definitions
│   │   └── providers/
│   │       ├── AuthProvider.tsx          # Auth context (JWT, user state)
│   │       ├── QueryProvider.tsx         # TanStack Query client
│   │       └── ThemeProvider.tsx         # Shadcn theme
│   │
│   ├── pages/                           # Route-level page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── CoursePage.tsx
│   │   ├── ModulePage.tsx
│   │   ├── AssignmentPage.tsx
│   │   ├── GradebookPage.tsx
│   │   ├── CalendarPage.tsx
│   │   ├── NotificationsPage.tsx
│   │   └── admin/
│   │       ├── UserManagementPage.tsx
│   │       ├── SystemSettingsPage.tsx
│   │       └── AllCoursesPage.tsx
│   │
│   ├── features/                        # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   └── services/
│   │   │       └── authApi.ts           # OAuth + JWT refresh API calls
│   │   ├── courses/
│   │   │   ├── components/
│   │   │   │   ├── CourseCard.tsx
│   │   │   │   ├── CourseForm.tsx
│   │   │   │   ├── EnrollmentManager.tsx
│   │   │   │   └── ModuleList.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useCourses.ts
│   │   │   │   └── useModules.ts
│   │   │   └── services/
│   │   │       └── courseApi.ts
│   │   ├── assignments/
│   │   │   ├── components/
│   │   │   │   ├── AssignmentCard.tsx
│   │   │   │   ├── AssignmentForm.tsx
│   │   │   │   ├── SubmissionUpload.tsx
│   │   │   │   └── GradingPanel.tsx
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── announcements/
│   │   │   ├── components/
│   │   │   │   ├── AnnouncementFeed.tsx
│   │   │   │   └── AnnouncementEditor.tsx  # Tiptap editor
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── gradebook/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── calendar/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   └── notifications/
│   │       ├── components/
│   │       │   ├── NotificationBell.tsx
│   │       │   └── NotificationPanel.tsx
│   │       ├── hooks/
│   │       └── services/
│   │
│   ├── components/                      # Shared UI components
│   │   ├── ui/                          # Shadcn/ui components
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── AppShell.tsx
│   │   │   └── MobileNav.tsx
│   │   ├── FileUpload.tsx
│   │   ├── SearchInput.tsx
│   │   ├── DataTable.tsx
│   │   └── EmptyState.tsx
│   │
│   ├── hooks/                           # Shared hooks
│   │   ├── useDebounce.ts
│   │   └── useMediaQuery.ts
│   │
│   ├── lib/                             # Utilities
│   │   ├── api-client.ts                # Axios/fetch wrapper with JWT interceptor
│   │   ├── utils.ts                     # cn() helper, formatters
│   │   └── constants.ts
│   │
│   └── styles/
│       └── globals.css                  # Tailwind base + custom styles
│
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

### 7.2 Frontend Patterns

| Pattern | Implementation |
|---|---|
| **Feature-Based Modules** | Each feature (courses, assignments, etc.) is self-contained with its own components, hooks, and API services |
| **Custom Hooks** | All API calls wrapped in TanStack Query hooks (e.g., `useCourses()`, `useAssignments()`) |
| **API Client** | Centralized Axios/fetch instance with JWT interceptor for auto-refresh |
| **Protected Routes** | Route guards via `AuthProvider` — redirect to login if unauthenticated, restrict by role |
| **Optimistic Updates** | TanStack Query mutations with optimistic cache updates for responsive UX |

### 7.3 Layout Structure

```mermaid
flowchart LR
    subgraph AppShell
        direction TB
        Header["🔝 Header (Logo · Search · Notifications · Avatar)"]
        subgraph Body["Main Body"]
            direction LR
            Sidebar["📋 Sidebar (Courses · Calendar · Settings)"]
            Content["📄 Content Area (Page Router Outlet)"]
        end
    end
```

- **Sidebar:** Collapsible, shows course list + navigation links. Collapses to icon-only on smaller screens. Hidden behind hamburger on mobile.
- **Header:** App logo, search bar, notification bell (with unread count badge), user avatar with dropdown (profile, logout).

---

## 8. Database Schema

### 8.1 Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ ENROLLMENT : "enrolled in"
    USER ||--o{ COURSE : "teaches"
    USER ||--o{ SUBMISSION : "submits"
    USER ||--o{ NOTIFICATION : "receives"
    COURSE ||--o{ MODULE : "contains"
    COURSE ||--o{ ENROLLMENT : "has"
    COURSE ||--o{ ANNOUNCEMENT : "has"
    COURSE ||--o{ CALENDAR_EVENT : "has"
    MODULE ||--o{ ASSIGNMENT : "contains"
    MODULE ||--o{ FILE_RESOURCE : "contains"
    ASSIGNMENT ||--o{ SUBMISSION : "receives"
    ANNOUNCEMENT ||--o{ ANNOUNCEMENT_ATTACHMENT : "has"

    USER {
        uuid id PK
        string email UK
        string full_name
        string avatar_url
        enum role "admin | teacher | student"
        string student_id "nullable"
        string google_id UK
        timestamp created_at
        timestamp updated_at
    }

    COURSE {
        uuid id PK
        string title
        string code UK
        text description
        string semester
        string cover_image_url "nullable"
        uuid teacher_id FK
        timestamp created_at
        timestamp updated_at
    }

    MODULE {
        uuid id PK
        string title
        text description "nullable"
        int sort_order
        uuid course_id FK
        timestamp created_at
    }

    ENROLLMENT {
        uuid id PK
        uuid user_id FK
        uuid course_id FK
        enum method "pool | invite"
        timestamp enrolled_at
    }

    ASSIGNMENT {
        uuid id PK
        string title
        text description
        int total_points
        enum status "draft | published"
        timestamp due_date
        uuid module_id FK
        uuid course_id FK
        timestamp created_at
        timestamp updated_at
    }

    SUBMISSION {
        uuid id PK
        uuid assignment_id FK
        uuid student_id FK
        string file_url
        string file_name
        int file_size
        int grade "nullable"
        text feedback "nullable"
        timestamp submitted_at
        timestamp graded_at "nullable"
    }

    ANNOUNCEMENT {
        uuid id PK
        uuid course_id FK
        uuid author_id FK
        string title
        text content "rich text HTML"
        timestamp created_at
    }

    ANNOUNCEMENT_ATTACHMENT {
        uuid id PK
        uuid announcement_id FK
        string file_url
        string file_name
        int file_size
    }

    FILE_RESOURCE {
        uuid id PK
        uuid module_id FK
        uuid uploaded_by FK
        string file_url
        string file_name
        string file_type
        int file_size
        timestamp uploaded_at
    }

    NOTIFICATION {
        uuid id PK
        uuid user_id FK
        enum type "announcement | assignment | grade | enrollment | reminder"
        string title
        text message
        string link "nullable, deep link to relevant page"
        boolean is_read
        timestamp created_at
    }

    CALENDAR_EVENT {
        uuid id PK
        uuid course_id FK
        uuid created_by FK
        string title
        text description "nullable"
        timestamp event_datetime
        enum source "auto | manual"
        uuid assignment_id FK "nullable, for auto events"
        timestamp created_at
    }

    REFRESH_TOKEN {
        uuid id PK
        uuid user_id FK
        string token_hash
        timestamp expires_at
        boolean is_revoked
        timestamp created_at
    }
```

### 8.2 Key Schema Notes

- All primary keys are **UUIDs** (v4) — no sequential IDs exposed
- `ENROLLMENT` has a **unique constraint** on `(user_id, course_id)` — no duplicate enrollments
- `SUBMISSION` keeps **all submissions** (not just the latest) — the latest non-graded submission is what the teacher sees, but history is preserved
- `CALENDAR_EVENT` with `source = 'auto'` is system-generated from assignment due dates; `source = 'manual'` is teacher-created
- `REFRESH_TOKEN` stores hashed tokens — never store raw refresh tokens
- All `text` fields containing user-generated rich text are **sanitized with bleach** before storage
- Timestamps use **UTC** (`TIMESTAMP WITH TIME ZONE`)

---

## 9. API Design

### 9.1 Base URL

$$
\texttt{BASE\_URL} = \texttt{https://api.openlms.app/api/v1}
$$

### 9.2 Endpoint Map

#### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/google` | Initiate Google OAuth flow | Public |
| `POST` | `/auth/google/callback` | Handle OAuth callback, return JWT pair | Public |
| `POST` | `/auth/refresh` | Refresh access token | Refresh Token |
| `POST` | `/auth/logout` | Revoke refresh token | Bearer |
| `GET` | `/auth/me` | Get current user profile | Bearer |

#### Users (Admin)
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/users` | List all users (paginated, filterable) | Admin |
| `GET` | `/users/{id}` | Get user details | Admin |
| `PUT` | `/users/{id}` | Update user (role, status) | Admin |
| `DELETE` | `/users/{id}` | Deactivate user | Admin |
| `POST` | `/users/bulk-import` | Import users from CSV | Admin |

#### Courses
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/courses` | Create course | Teacher |
| `GET` | `/courses` | List user's courses | Bearer |
| `GET` | `/courses/search?q=` | Search courses by name/code | Bearer |
| `GET` | `/courses/{id}` | Get course details | Enrolled/Teacher |
| `PUT` | `/courses/{id}` | Update course | Teacher (owner) |
| `DELETE` | `/courses/{id}` | Delete course | Teacher (owner) |

#### Enrollment
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/courses/{id}/enroll` | Enroll student(s) from pool | Teacher (owner) |
| `POST` | `/courses/{id}/invite` | Invite student by email | Teacher (owner) |
| `GET` | `/courses/{id}/students` | List enrolled students | Teacher (owner) |
| `DELETE` | `/courses/{id}/students/{userId}` | Remove student | Teacher (owner) |

#### Modules
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/courses/{courseId}/modules` | Create module | Teacher (owner) |
| `GET` | `/courses/{courseId}/modules` | List modules (ordered) | Enrolled/Teacher |
| `PUT` | `/modules/{id}` | Update module | Teacher (owner) |
| `DELETE` | `/modules/{id}` | Delete module | Teacher (owner) |
| `PATCH` | `/modules/{id}/reorder` | Update sort order | Teacher (owner) |

#### Assignments
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/modules/{moduleId}/assignments` | Create assignment (draft) | Teacher |
| `GET` | `/courses/{courseId}/assignments` | List all assignments in course | Enrolled/Teacher |
| `GET` | `/assignments/{id}` | Get assignment details | Enrolled/Teacher |
| `PUT` | `/assignments/{id}` | Update assignment | Teacher |
| `PATCH` | `/assignments/{id}/publish` | Publish assignment | Teacher |
| `DELETE` | `/assignments/{id}` | Delete assignment | Teacher |

#### Submissions
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/assignments/{id}/submissions` | Submit file | Student (enrolled) |
| `GET` | `/assignments/{id}/submissions` | List all submissions (teacher) | Teacher |
| `GET` | `/assignments/{id}/submissions/mine` | Get own submissions | Student |
| `GET` | `/submissions/{id}` | Get submission details | Teacher/Owner |

#### Grading
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/submissions/{id}/grade` | Grade a submission | Teacher |
| `GET` | `/courses/{id}/gradebook` | Get gradebook (all students × assignments) | Teacher |
| `GET` | `/courses/{id}/gradebook/export` | Download CSV | Teacher |
| `GET` | `/courses/{id}/grades/mine` | Get own grades | Student |

#### Announcements
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/courses/{id}/announcements` | Create announcement | Teacher |
| `GET` | `/courses/{id}/announcements` | List announcements | Enrolled/Teacher |
| `GET` | `/announcements/{id}` | Get announcement details | Enrolled/Teacher |
| `PUT` | `/announcements/{id}` | Update announcement | Teacher |
| `DELETE` | `/announcements/{id}` | Delete announcement | Teacher |

#### Calendar
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/courses/{id}/calendar` | Get course calendar events | Enrolled/Teacher |
| `POST` | `/courses/{id}/calendar` | Create manual event | Teacher |
| `PUT` | `/calendar/{id}` | Update event | Teacher |
| `DELETE` | `/calendar/{id}` | Delete manual event | Teacher |
| `GET` | `/calendar` | Aggregated calendar (all courses) | Bearer |

#### Notifications
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/notifications` | List user's notifications | Bearer |
| `PATCH` | `/notifications/{id}/read` | Mark as read | Bearer |
| `PATCH` | `/notifications/read-all` | Mark all as read | Bearer |
| `GET` | `/notifications/unread-count` | Get unread count | Bearer |

### 9.3 Standard Response Format

**Success:**
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

**Error:**
```json
{
  "detail": "Assignment not found",
  "code": "ASSIGNMENT_NOT_FOUND",
  "status": 404
}
```

### 9.4 Pagination

All list endpoints support cursor-based or offset pagination:

$$
\texttt{GET /api/v1/courses?page=2\&per\_page=20}
$$

Default: `page=1`, `per_page=20`, max `per_page=100`

---

## 10. Authentication & Security

### 10.1 Authentication Flow

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend (React)
    participant B as Backend (FastAPI)
    participant G as Google OAuth

    U->>F: Click "Sign in with Google"
    F->>B: POST /auth/google
    B->>G: Redirect to Google consent screen
    G->>B: Authorization code callback
    B->>G: Exchange code for Google tokens
    G-->>B: Google user info (email, name, avatar)
    B->>B: Find or create user in DB
    B->>B: Generate JWT access + refresh tokens
    B-->>F: Return { access_token, refresh_token, user }
    F->>F: Store tokens (httpOnly cookie or secure storage)
    F->>B: API requests with Authorization: Bearer <access_token>

    Note over F,B: When access token expires (15 min):
    F->>B: POST /auth/refresh { refresh_token }
    B->>B: Validate & rotate refresh token
    B-->>F: New { access_token, refresh_token }
```

### 10.2 JWT Structure

**Access Token Payload:**
```json
{
  "sub": "uuid-user-id",
  "email": "user@university.edu",
  "role": "teacher",
  "exp": 1700000000,
  "iat": 1699999100,
  "type": "access"
}
```

**Refresh Token:** Opaque string stored as a **hashed value** in the `REFRESH_TOKEN` table. Rotated on every use (old token invalidated, new token issued).

### 10.3 Security Measures

| Measure | Implementation |
|---|---|
| **CORS** | Environment-driven `ALLOWED_ORIGINS` — strict in production, permissive in development |
| **Input Validation** | All inputs validated via **Pydantic** models with strict type checking and field constraints |
| **HTML Sanitization** | All rich-text fields sanitized with **bleach** before database storage (prevent XSS) |
| **SQL Injection** | Prevented by **SQLAlchemy parameterized queries** — never raw string interpolation |
| **RBAC** | Enforced at the route level via FastAPI `Depends()` guards (`require_admin`, `require_teacher`, etc.) |
| **Rate Limiting** | PaaS-level DDoS protection (Render/Netlify) — app-level rate limiting in Phase 2 |
| **File Validation** | Validate file extension against allowed types list; enforce 25MB size limit server-side |
| **Token Storage** | Refresh tokens stored as **bcrypt hashes** — never plaintext |
| **HTTPS** | Enforced at PaaS level (Netlify and Render provide automatic TLS) |
| **Secrets Management** | All secrets via environment variables — `.env` gitignored, `.env.example` committed |
| **UUID PKs** | No sequential integer IDs exposed — prevents enumeration attacks |

### 10.4 RBAC Dependency Chain

```python
# presentation/dependencies/auth.py

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT, fetch user from DB, return User entity."""
    ...

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, detail="Admin access required")
    return user

async def require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("teacher", "admin"):
        raise HTTPException(403, detail="Teacher access required")
    return user

async def require_enrolled(
    course_id: UUID,
    user: User = Depends(get_current_user),
    enrollment_repo: IEnrollmentRepository = Depends(get_enrollment_repo)
) -> User:
    """Verify user is enrolled in the course or is the teacher/admin."""
    ...
```

---

## 11. Infrastructure & Deployment

### 11.1 Deployment Architecture

```mermaid
flowchart LR
    subgraph Client
        Browser["🌐 Browser"]
    end

    subgraph Netlify["Netlify"]
        FE["React SPA (Static)"]
    end

    subgraph Render["Render"]
        BE["FastAPI Server"]
    end

    subgraph Supabase["Supabase"]
        DB["PostgreSQL"]
        Storage["File Storage"]
    end

    subgraph Resend["Resend"]
        Email["Email API"]
    end

    subgraph Google["Google"]
        OAuth["OAuth 2.0"]
    end

    Browser --> FE
    FE --> BE
    BE --> DB
    BE --> Storage
    BE --> Email
    BE --> OAuth
```

### 11.2 Environment Variables

**Backend (`.env.example`):**
```env
# App
APP_NAME=OpenLMS
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/openlms

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Resend
RESEND_API_KEY=your-resend-api-key
EMAIL_FROM=noreply@openlms.app

# CORS
ALLOWED_ORIGINS=http://localhost:5173

# File Upload
MAX_FILE_SIZE_MB=25
```

**Frontend (`.env.example`):**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_GOOGLE_CLIENT_ID=your-client-id
VITE_APP_NAME=OpenLMS
```

### 11.3 CI/CD (MVP)

- **Netlify:** Auto-deploy frontend on push to `main` branch
- **Render:** Auto-deploy backend on push to `main` branch
- **Branch previews:** Both platforms support preview deployments on PRs
- **Phase 2:** Add GitHub Actions for linting (Ruff, ESLint), testing (pytest, Vitest), and build checks

### 11.4 Future Migration Path

$$
\text{PaaS (MVP)} \xrightarrow{\text{Phase 3}} \text{AWS / GCP}
$$

The architecture is migration-ready:
- Supabase Storage is **S3-compatible** → swap to AWS S3 with config change
- Supabase PostgreSQL → AWS RDS or Cloud SQL (standard pg_dump migration)
- Render → AWS ECS/Fargate or GCP Cloud Run (containerize with Dockerfile)
- Netlify → AWS CloudFront + S3 or GCP Cloud CDN

---

## 12. Phased Roadmap

### Phase 1 — MVP ✅ *Build Now*

| Feature | Description |
|---|---|
| Google OAuth Login | Single sign-on with JWT token pair |
| Admin User Management | CRUD, bulk CSV import, role assignment |
| Course Management | Create, edit, delete courses |
| Module Management | Create ordered modules within courses |
| Student Enrollment | From admin pool + email invite |
| Assignments | Create (draft/publish), file submission, resubmission |
| Grading | Points-based grading, gradebook view, CSV export |
| Announcements | Rich text (Tiptap) + file attachments |
| Calendar | Auto due dates + manual teacher events |
| Notifications | In-app (bell + panel) + email (Resend) |
| Course Search | Basic search by name/code |
| Dashboard | Courses + deadlines + recent announcements |
| Responsive UI | Sidebar + header layout, mobile-friendly |
| Seed Script | Full dev dataset for demos and contributors |

### Phase 2 — Feature Expansion

| Feature | Description |
|---|---|
| Quizzes & Assessments | Multiple choice, true/false, short answer |
| Discussion Forums | Threaded discussions per course |
| Real-Time Notifications | WebSockets or SSE for live updates |
| Role-Specific Dashboards | Tailored views per role |
| Grade Weighting | Category-based weighting (Homework 30%, Exams 50%) |
| Manual Grade Overrides | Direct gradebook editing |
| Rubrics | Attach scoring rubrics to assignments |
| Extended Submissions | Text, link, and code submissions |
| File Content Validation | MIME type verification |
| App-Level Rate Limiting | Redis-backed per-user rate limits |
| GitHub Actions CI/CD | Lint + test + build on PR |
| Notification Preferences | User controls which events trigger email |
| Global Search | Full-text search across all content |
| Data Privacy Compliance | Formal DPA/FERPA/GDPR audit |

### Phase 3 — Platform Maturity

| Feature | Description |
|---|---|
| Attendance Tracking | Mark and report attendance |
| Video Conferencing | Zoom/Google Meet integration |
| Mobile Apps / PWA | Native or installable web app |
| Analytics Dashboard | Admin insights and reporting |
| Audit Logs | Track all system actions |
| Custom Roles & Permissions | Admin-configurable roles |
| Internationalization | Multi-language support (react-i18next) |
| Cloud Migration | Move to AWS or GCP infrastructure |

---

## 13. Development Standards

### 13.1 Code Style

| Language | Linter / Formatter | Config |
|---|---|---|
| Python | **Ruff** (linter + formatter) | `pyproject.toml` |
| TypeScript | **ESLint** + **Prettier** | `.eslintrc.js`, `.prettierrc` |
| CSS | **Tailwind** (utility-first, no custom CSS unless necessary) | `tailwind.config.ts` |

### 13.2 Git Conventions

| Convention | Standard |
|---|---|
| Branch naming | `feature/`, `fix/`, `chore/` prefixes (e.g., `feature/assignment-grading`) |
| Commit messages | Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`) |
| PR workflow | Feature branch → PR to `main` → Review → Merge |

### 13.3 Testing

| Layer | Tool | Scope |
|---|---|---|
| Backend unit tests | **pytest** | Service layer (use cases), utility functions |
| Backend integration tests | **pytest** + **httpx** | API route testing with test database |
| Fixtures | **conftest.py** | Shared test database, mock users, sample data |

$$
\text{MVP Test Coverage Target} \geq 70\% \text{ (backend)}
$$

### 13.4 Seed Script

`seed.py` must create:
- 1 Admin user
- 3 Teacher users
- 20 Student users
- 5 Courses (with 3–5 modules each)
- 15+ Assignments (mix of draft and published, various due dates)
- Sample submissions and grades
- Sample announcements with attachments
- Calendar events

> [!TIP]
> The seed script should be idempotent — safe to run multiple times without duplicating data. Use `upsert` or check-before-insert patterns.

---

## 14. Appendix

### 14.1 Allowed File Types

```
PDF, DOCX, PPTX, XLSX, JPG, JPEG, PNG, ZIP, MP4, MP3, CSV, TXT
```

$$
\text{Max File Size} = 25 \text{ MB} = 25 \times 1024 \times 1024 \text{ bytes} = 26{,}214{,}400 \text{ bytes}
$$

### 14.2 Notification Email Templates

Templates built with **React Email** (rendered server-side via Resend):

| Template | Trigger |
|---|---|
| `enrollment-welcome` | Student added to a course |
| `new-announcement` | Teacher posts an announcement |
| `new-assignment` | Teacher publishes an assignment |
| `assignment-graded` | Teacher grades a submission |
| `due-date-reminder` | 24 hours before assignment due date |
| `course-invite` | Teacher invites student by email |

### 14.3 Error Code Reference

| Code | HTTP Status | Description |
|---|---|---|
| `AUTH_INVALID_TOKEN` | 401 | JWT is expired, malformed, or revoked |
| `AUTH_INSUFFICIENT_ROLE` | 403 | User's role cannot access this resource |
| `RESOURCE_NOT_FOUND` | 404 | Requested entity does not exist |
| `ENROLLMENT_DUPLICATE` | 409 | Student is already enrolled in this course |
| `FILE_TOO_LARGE` | 413 | File exceeds 25MB limit |
| `FILE_TYPE_NOT_ALLOWED` | 415 | File extension not in allowed list |
| `VALIDATION_ERROR` | 422 | Request body failed Pydantic validation |
| `ASSIGNMENT_PAST_DUE` | 400 | Submission after due date |
| `ASSIGNMENT_NOT_PUBLISHED` | 400 | Cannot submit to a draft assignment |
| `SERVER_ERROR` | 500 | Unexpected internal error |

### 14.4 Third-Party Dependencies

**Backend (Python):**
| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy[asyncio]` | ORM |
| `alembic` | Database migrations |
| `asyncpg` | Async PostgreSQL driver |
| `pydantic[email]` | Data validation |
| `pydantic-settings` | Configuration management |
| `python-jose[cryptography]` | JWT encoding/decoding |
| `httpx` | HTTP client (Google OAuth, Resend) |
| `bleach` | HTML sanitization |
| `python-multipart` | File upload handling |
| `resend` | Email delivery |
| `supabase` | Supabase client (Storage) |

**Frontend (TypeScript):**
| Package | Purpose |
|---|---|
| `react` + `react-dom` | UI framework |
| `react-router-dom` | Routing |
| `@tanstack/react-query` | Server state management |
| `axios` | HTTP client |
| `@tiptap/react` | Rich text editor |
| `tailwindcss` | Utility CSS |
| `shadcn/ui` | Component library |
| `lucide-react` | Icons |
| `date-fns` | Date formatting |
| `react-email` | Email templates (dev) |
| `zod` | Schema validation (forms) |
| `react-hook-form` | Form handling |
| `@hookform/resolvers` | Zod + React Hook Form bridge |
| `sonner` | Toast notifications |

---

> [!NOTE]
> This PRD was generated through an exhaustive design interview covering **40+ decisions** across 6 rounds. Every branch of the design tree was visited — nothing was silently assumed. The implementing agent should treat Phase 1 features as **mandatory scope** and Phases 2–3 as **documented backlog**.

---

*OpenLMS — Apache 2.0 Licensed · PRD v1.0 · 2026-11-14*
