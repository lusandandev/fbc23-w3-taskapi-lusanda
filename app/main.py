import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router
from app.routes.task_routes import router as task_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("task_api.requests")

app = FastAPI(
    title="Task Tracker API",
    description="A containerised task tracker API backed by PostgreSQL.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(health_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        # The registered server-error handler logs the traceback; re-raise so
        # it can return the generic response while this middleware records 500.
        raise
    finally:
        duration_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )


@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError):
    # Return 400 as specified, and omit Pydantic's `input` values so passwords
    # and other submitted data are never echoed to the client.
    errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())[1:]),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": errors})


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logger.exception("Unexpected server error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred"},
    )
