"""
Request monitoring middleware for FiscIA Pro.
Tracks timing, correlation IDs, and feeds Prometheus metrics.
"""
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fiscia.logging_config import new_correlation_id
from fiscia.metrics import (
    ERROR_COUNT,
    REQUEST_COUNT,
    REQUEST_DURATION,
    REQUESTS_IN_PROGRESS,
)

logger = logging.getLogger("fiscia.monitoring")


def _route_label(request: Request) -> str:
    """Extract a stable route pattern (avoids high-cardinality path params)."""
    if request.scope.get("route"):
        return request.scope["route"].path
    return request.url.path


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware that instruments every HTTP request with metrics and logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Correlation ID: prefer incoming header, else generate
        cid = request.headers.get("X-Correlation-ID") or new_correlation_id()
        from fiscia.logging_config import correlation_id_var
        correlation_id_var.set(cid)

        method = request.method
        endpoint = _route_label(request)
        client_ip = request.client.host if request.client else "-"

        REQUESTS_IN_PROGRESS.labels(method=method).inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start
            ERROR_COUNT.labels(error_type=type(exc).__name__, module="http").inc()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code="500").inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            logger.error(
                "Unhandled exception",
                extra={
                    "method": method,
                    "path": endpoint,
                    "status_code": 500,
                    "duration_ms": round(duration * 1000, 2),
                    "client_ip": client_ip,
                },
                exc_info=exc,
            )
            raise
        finally:
            REQUESTS_IN_PROGRESS.labels(method=method).dec()

        duration = time.perf_counter() - start
        status = response.status_code

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=str(status)).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        if status >= 400:
            ERROR_COUNT.labels(
                error_type=f"http_{status}",
                module="http",
            ).inc()

        # Structured access log
        log_level = logging.WARNING if status >= 400 else logging.INFO
        logger.log(
            log_level,
            "%s %s %d %.0fms",
            method,
            endpoint,
            status,
            duration * 1000,
            extra={
                "method": method,
                "path": endpoint,
                "status_code": status,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": client_ip,
            },
        )

        # Attach correlation ID to response for client tracing
        response.headers["X-Correlation-ID"] = cid
        return response
