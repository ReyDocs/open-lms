import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings

from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .course_routes import router as course_router
from .module_routes import router as module_router
from .assignment_routes import router as assignment_router
from .submission_routes import router as submission_router
from .announcement_routes import router as announcement_router
from .grading_routes import router as grading_router
from .calendar_routes import router as calendar_router
from .notification_routes import router as notification_router
from .admin_routes import router as admin_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(course_router)
api_v1_router.include_router(module_router)
api_v1_router.include_router(assignment_router)
api_v1_router.include_router(submission_router)
api_v1_router.include_router(announcement_router)
api_v1_router.include_router(grading_router)
api_v1_router.include_router(calendar_router)
api_v1_router.include_router(notification_router)
api_v1_router.include_router(admin_router)


# File download / streaming route for local storage fallback
@api_v1_router.get("/files/{bucket}/{filename}")
async def serve_file(bucket: str, filename: str):
    file_path = os.path.join(settings.upload_dir, bucket, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
