"""
Prometheus metrics for FiscIA Pro.
Exposes request counts, durations, error rates, and business metrics.
"""
from prometheus_client import Counter, Histogram, Gauge, Info

# --- HTTP request metrics ---

REQUEST_COUNT = Counter(
    "fiscia_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "fiscia_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

REQUESTS_IN_PROGRESS = Gauge(
    "fiscia_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method"],
)

# --- Error metrics ---

ERROR_COUNT = Counter(
    "fiscia_errors_total",
    "Total application errors",
    ["error_type", "module"],
)

# --- Business metrics ---

IS_CALCULATIONS = Counter(
    "fiscia_is_calculations_total",
    "Total IS tax calculations performed",
    ["regime"],
)

LIASSE_CALCULATIONS = Counter(
    "fiscia_liasse_calculations_total",
    "Total liasse 2058-A calculations performed",
    ["regime", "saved"],
)

MERE_FILIALE_CHECKS = Counter(
    "fiscia_mere_filiale_checks_total",
    "Total mere-filiale Art. 145 eligibility checks",
    ["eligible"],
)

CGI_SEARCHES = Counter(
    "fiscia_cgi_searches_total",
    "Total CGI article searches",
)

AUDIT_LOG_ENTRIES = Counter(
    "fiscia_audit_log_entries_total",
    "Total audit log entries written",
    ["action"],
)

# --- Database metrics ---

DB_QUERY_DURATION = Histogram(
    "fiscia_db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

# --- App info ---

APP_INFO = Info(
    "fiscia_app",
    "FiscIA Pro application metadata",
)
APP_INFO.info({"version": "3.0", "engine": "pure_python", "framework": "fastapi"})
