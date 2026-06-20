# ============================================================
#         StudyBuddyV3BOT — Database Package Init
#         Exposes database manager and repositories
#         at package level for clean imports
# ============================================================

from database.connection import db_manager, get_database, get_collection
from database.models import (
    UserModel,
    NoteModel,
    AIContextModel,
    AdminLogModel,
    BroadcastModel,
    APIStatsModel,
)
from database.repositories.user_repo import UserRepository
from database.repositories.notes_repo import NotesRepository
from database.repositories.admin_repo import AdminRepository

# ---------------------------------------------------------------------------
# Pre-instantiated repository singletons
# Ready to import and use anywhere in the project
# ---------------------------------------------------------------------------
user_repo  = UserRepository()
notes_repo = NotesRepository()
admin_repo = AdminRepository()

__all__ = [
    # ── Connection ──
    "db_manager",           # MongoDB connection manager
    "get_database",         # Returns active database instance
    "get_collection",       # Returns a named collection

    # ── Models / Schemas ──
    "UserModel",            # User document schema
    "NoteModel",            # Note document schema
    "AIContextModel",       # AI conversation context schema
    "AdminLogModel",        # Admin action log schema
    "BroadcastModel",       # Broadcast record schema
    "APIStatsModel",        # API usage stats schema

    # ── Repositories ──
    "UserRepository",       # User CRUD class
    "NotesRepository",      # Notes CRUD class
    "AdminRepository",      # Admin stats & logs class

    # ── Singletons ──
    "user_repo",            # Ready-to-use user repository instance
    "notes_repo",           # Ready-to-use notes repository instance
    "admin_repo",           # Ready-to-use admin repository instance
]