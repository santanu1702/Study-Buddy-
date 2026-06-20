# ============================================================
#         StudyBuddyV3BOT — Repositories Package Init
#         Exposes all repository classes and singletons
#         for clean imports across the project
# ============================================================

from database.repositories.user_repo import UserRepository
from database.repositories.notes_repo import NotesRepository
from database.repositories.admin_repo import AdminRepository

# ---------------------------------------------------------------------------
# Pre-instantiated singletons — import and use directly anywhere
# ---------------------------------------------------------------------------
user_repo  = UserRepository()
notes_repo = NotesRepository()
admin_repo = AdminRepository()

__all__ = [
    # ── Repository Classes ──
    "UserRepository",       # Full user CRUD + ban management
    "NotesRepository",      # Full notes CRUD + pagination
    "AdminRepository",      # Admin stats, logs, broadcasts

    # ── Ready-to-use Singletons ──
    "user_repo",            # Use: from database.repositories import user_repo
    "notes_repo",           # Use: from database.repositories import notes_repo
    "admin_repo",           # Use: from database.repositories import admin_repo
]