from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    code = "ERROR"
    if exc.status_code == 401:
        code = "AUTH_INVALID_TOKEN"
    elif exc.status_code == 403:
        code = "AUTH_INSUFFICIENT_ROLE"
    elif exc.status_code == 404:
        code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == 409:
        code = "CONFLICT"
    elif exc.status_code == 413:
        code = "FILE_TOO_LARGE"
    elif exc.status_code == 415:
        code = "FILE_TYPE_NOT_ALLOWED"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": code,
            "status": exc.status_code,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=422,
        content={
            "detail": msg,
            "code": "VALIDATION_ERROR",
            "status": 422,
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {exc}")
    status_code = 500
    code = "SERVER_ERROR"
    detail = str(exc)

    if isinstance(exc, ValueError):
        status_code = 400
        code = "BAD_REQUEST"
    elif isinstance(exc, PermissionError):
        status_code = 403
        code = "AUTH_INSUFFICIENT_ROLE"

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "code": code,
            "status": status_code,
        },
    )
