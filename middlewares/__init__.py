# ============================================================
#         StudyBuddyV3BOT — Middlewares Package Init
#         Exposes all middleware classes at package level
#         for clean imports in main.py
# ============================================================

from middlewares.auth_middleware        import AuthMiddleware
from middlewares.rate_limit_middleware  import RateLimitMiddleware
from middlewares.maintenance_middleware import MaintenanceMiddleware

__all__ = [
    # ── Middleware Classes ──
    "AuthMiddleware",          # Ban check + user registration + language load
    "RateLimitMiddleware",     # Anti-spam — per-user message rate limiting
    "MaintenanceMiddleware",   # Maintenance mode gate — blocks non-admins
]