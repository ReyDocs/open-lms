from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
from app.infrastructure.repositories.sqlalchemy_course_repo import SQLAlchemyCourseRepository
from app.infrastructure.repositories.sqlalchemy_module_repo import SQLAlchemyModuleRepository
from app.infrastructure.repositories.sqlalchemy_assignment_repo import SQLAlchemyAssignmentRepository
from app.infrastructure.repositories.sqlalchemy_submission_repo import SQLAlchemySubmissionRepository
from app.infrastructure.repositories.sqlalchemy_announcement_repo import SQLAlchemyAnnouncementRepository
from app.infrastructure.repositories.sqlalchemy_notification_repo import SQLAlchemyNotificationRepository
from app.infrastructure.repositories.sqlalchemy_calendar_event_repo import SQLAlchemyCalendarEventRepository
from app.infrastructure.repositories.sqlalchemy_enrollment_repo import SQLAlchemyEnrollmentRepository
from app.infrastructure.repositories.sqlalchemy_refresh_token_repo import SQLAlchemyRefreshTokenRepository

from app.infrastructure.security.jwt_handler import JWTHandler
from app.infrastructure.external.supabase_storage_service import SupabaseStorageService
from app.infrastructure.external.resend_email_service import ResendEmailService
from app.infrastructure.external.google_oauth_service import GoogleOAuthService

from app.application.services.user_service import UserService
from app.application.services.course_service import CourseService
from app.application.services.module_service import ModuleService
from app.application.services.assignment_service import AssignmentService
from app.application.services.submission_service import SubmissionService
from app.application.services.announcement_service import AnnouncementService
from app.application.services.grading_service import GradingService
from app.application.services.calendar_service import CalendarService
from app.application.services.notification_service import NotificationService
from app.application.services.enrollment_service import EnrollmentService

# Singletons / adapter instances
jwt_handler = JWTHandler()
storage_service = SupabaseStorageService()
email_service = ResendEmailService()
google_oauth_service = GoogleOAuthService()


def get_jwt_handler() -> JWTHandler:
    return jwt_handler


def get_storage_service() -> SupabaseStorageService:
    return storage_service


def get_email_service() -> ResendEmailService:
    return email_service


def get_google_oauth_service() -> GoogleOAuthService:
    return google_oauth_service


# Repository DI
def get_user_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_course_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyCourseRepository:
    return SQLAlchemyCourseRepository(db)


def get_module_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyModuleRepository:
    return SQLAlchemyModuleRepository(db)


def get_assignment_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyAssignmentRepository:
    return SQLAlchemyAssignmentRepository(db)


def get_submission_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemySubmissionRepository:
    return SQLAlchemySubmissionRepository(db)


def get_announcement_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyAnnouncementRepository:
    return SQLAlchemyAnnouncementRepository(db)


def get_notification_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyNotificationRepository:
    return SQLAlchemyNotificationRepository(db)


def get_calendar_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyCalendarEventRepository:
    return SQLAlchemyCalendarEventRepository(db)


def get_enrollment_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyEnrollmentRepository:
    return SQLAlchemyEnrollmentRepository(db)


def get_refresh_token_repo(db: AsyncSession = Depends(get_db)) -> SQLAlchemyRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(db)


# Service DI
def get_notification_service(
    notif_repo: SQLAlchemyNotificationRepository = Depends(get_notification_repo),
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
    email_svc: ResendEmailService = Depends(get_email_service),
) -> NotificationService:
    return NotificationService(notif_repo, enrollment_repo, email_svc)


def get_user_service(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo)


def get_course_service(
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> CourseService:
    return CourseService(course_repo, user_repo)


def get_module_service(
    module_repo: SQLAlchemyModuleRepository = Depends(get_module_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    storage_svc: SupabaseStorageService = Depends(get_storage_service),
) -> ModuleService:
    return ModuleService(module_repo, course_repo, storage_svc)


def get_assignment_service(
    assignment_repo: SQLAlchemyAssignmentRepository = Depends(get_assignment_repo),
    module_repo: SQLAlchemyModuleRepository = Depends(get_module_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    calendar_repo: SQLAlchemyCalendarEventRepository = Depends(get_calendar_repo),
    notification_svc: NotificationService = Depends(get_notification_service),
) -> AssignmentService:
    return AssignmentService(assignment_repo, module_repo, course_repo, calendar_repo, notification_svc)


def get_submission_service(
    submission_repo: SQLAlchemySubmissionRepository = Depends(get_submission_repo),
    assignment_repo: SQLAlchemyAssignmentRepository = Depends(get_assignment_repo),
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    storage_svc: SupabaseStorageService = Depends(get_storage_service),
) -> SubmissionService:
    return SubmissionService(submission_repo, assignment_repo, enrollment_repo, user_repo, storage_svc)


def get_grading_service(
    submission_repo: SQLAlchemySubmissionRepository = Depends(get_submission_repo),
    assignment_repo: SQLAlchemyAssignmentRepository = Depends(get_assignment_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    notification_svc: NotificationService = Depends(get_notification_service),
) -> GradingService:
    return GradingService(submission_repo, assignment_repo, course_repo, enrollment_repo, user_repo, notification_svc)


def get_announcement_service(
    announcement_repo: SQLAlchemyAnnouncementRepository = Depends(get_announcement_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    notification_svc: NotificationService = Depends(get_notification_service),
) -> AnnouncementService:
    return AnnouncementService(announcement_repo, course_repo, user_repo, notification_svc)


def get_calendar_service(
    calendar_repo: SQLAlchemyCalendarEventRepository = Depends(get_calendar_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
) -> CalendarService:
    return CalendarService(calendar_repo, course_repo)


def get_enrollment_service(
    enrollment_repo: SQLAlchemyEnrollmentRepository = Depends(get_enrollment_repo),
    course_repo: SQLAlchemyCourseRepository = Depends(get_course_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    email_svc: ResendEmailService = Depends(get_email_service),
) -> EnrollmentService:
    return EnrollmentService(enrollment_repo, course_repo, user_repo, email_svc)
