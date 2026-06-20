# ============================================================
#         StudyBuddyV3BOT — Database Models / Schemas
#         Dataclass-based document schemas for MongoDB
#         Provides type safety, defaults, and serialization
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum

from config.constants import (
    UserRole,
    NoteStatus,
    Language,
)


# ============================================================
#   HELPER FUNCTIONS
# ============================================================

def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def utcnow_naive() -> datetime:
    """
    Return current UTC datetime (timezone-naive).
    MongoDB stores naive datetimes — use this for DB fields.
    """
    return datetime.utcnow()


# ============================================================
#   USER MODEL
#   Represents a registered bot user in the database
# ============================================================

@dataclass
class UserModel:
    """
    Represents a bot user document in the 'users' collection.

    Created automatically when a user sends /start for the first time.
    Updated on every interaction (last_active, message_count).
    """

    # ── Identity ──
    user_id:        int                         # Telegram user ID (unique)
    username:       Optional[str]  = None       # Telegram @username (nullable)
    first_name:     str            = ""         # Telegram first name
    last_name:      Optional[str]  = None       # Telegram last name (nullable)
    full_name:      str            = ""         # Computed: first + last

    # ── Access Control ──
    role:           str = UserRole.USER.value   # user | admin | banned
    is_banned:      bool = False                # Quick ban check flag
    ban_reason:     Optional[str] = None        # Reason for ban (if banned)
    banned_at:      Optional[datetime] = None   # When banned
    banned_by:      Optional[int] = None        # Admin ID who banned

    # ── Language ──
    language_code:  str = Language.ENGLISH.value  # en | hi | bn | ar
    telegram_lang:  Optional[str] = None           # Raw Telegram language_code

    # ── Activity Tracking ──
    message_count:  int      = 0               # Total messages sent
    ai_requests:    int      = 0               # Total AI questions asked
    notes_count:    int      = 0               # Current active notes count
    last_active:    datetime = field(
        default_factory=utcnow_naive
    )

    # ── Timestamps ──
    created_at:     datetime = field(
        default_factory=utcnow_naive
    )
    updated_at:     datetime = field(
        default_factory=utcnow_naive
    )

    # ── Settings ──
    notifications_enabled: bool = True         # Receive broadcast messages
    ai_context_enabled:    bool = True         # Keep AI conversation context

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        """
        Convert to MongoDB-compatible dictionary.
        Used when inserting a new user document.
        """
        return {
            "user_id":               self.user_id,
            "username":              self.username,
            "first_name":            self.first_name,
            "last_name":             self.last_name,
            "full_name":             self.full_name,
            "role":                  self.role,
            "is_banned":             self.is_banned,
            "ban_reason":            self.ban_reason,
            "banned_at":             self.banned_at,
            "banned_by":             self.banned_by,
            "language_code":         self.language_code,
            "telegram_lang":         self.telegram_lang,
            "message_count":         self.message_count,
            "ai_requests":           self.ai_requests,
            "notes_count":           self.notes_count,
            "last_active":           self.last_active,
            "created_at":            self.created_at,
            "updated_at":            self.updated_at,
            "notifications_enabled": self.notifications_enabled,
            "ai_context_enabled":    self.ai_context_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserModel":
        """
        Reconstruct a UserModel from a MongoDB document.
        Handles missing fields gracefully with defaults.
        """
        return cls(
            user_id=                data.get("user_id", 0),
            username=               data.get("username"),
            first_name=             data.get("first_name", ""),
            last_name=              data.get("last_name"),
            full_name=              data.get("full_name", ""),
            role=                   data.get("role", UserRole.USER.value),
            is_banned=              data.get("is_banned", False),
            ban_reason=             data.get("ban_reason"),
            banned_at=              data.get("banned_at"),
            banned_by=              data.get("banned_by"),
            language_code=          data.get("language_code", Language.ENGLISH.value),
            telegram_lang=          data.get("telegram_lang"),
            message_count=          data.get("message_count", 0),
            ai_requests=            data.get("ai_requests", 0),
            notes_count=            data.get("notes_count", 0),
            last_active=            data.get("last_active", utcnow_naive()),
            created_at=             data.get("created_at", utcnow_naive()),
            updated_at=             data.get("updated_at", utcnow_naive()),
            notifications_enabled=  data.get("notifications_enabled", True),
            ai_context_enabled=     data.get("ai_context_enabled", True),
        )

    @classmethod
    def from_telegram_user(cls, tg_user) -> "UserModel":
        """
        Create a UserModel from a python-telegram-bot User object.
        Used when registering a new user on /start.

        Args:
            tg_user: telegram.User object
        """
        full_name = tg_user.full_name or tg_user.first_name or "User"
        lang = Language.from_telegram_code(
            tg_user.language_code or "en"
        ).value

        return cls(
            user_id=       tg_user.id,
            username=      tg_user.username,
            first_name=    tg_user.first_name or "",
            last_name=     tg_user.last_name,
            full_name=     full_name,
            language_code= lang,
            telegram_lang= tg_user.language_code,
        )

    # ================================================================
    #   COMPUTED PROPERTIES
    # ================================================================

    @property
    def display_name(self) -> str:
        """Return best available display name."""
        if self.full_name:
            return self.full_name
        if self.username:
            return f"@{self.username}"
        return f"User#{self.user_id}"

    @property
    def is_admin(self) -> bool:
        """True if user has admin role."""
        return self.role == UserRole.ADMIN.value

    @property
    def mention(self) -> str:
        """Return Telegram markdown mention string."""
        return f"[{self.display_name}](tg://user?id={self.user_id})"

    def __repr__(self) -> str:
        return (
            f"UserModel(id={self.user_id}, "
            f"name={self.display_name}, "
            f"role={self.role})"
        )


# ============================================================
#   NOTE MODEL
#   Represents a saved study note
# ============================================================

@dataclass
class NoteModel:
    """
    Represents a user's saved note in the 'notes' collection.

    Notes are soft-deleted (status = "deleted") rather than
    permanently removed, allowing potential recovery.
    """

    # ── Identity ──
    note_id:    str                             # UUID string (unique)
    user_id:    int                             # Owner's Telegram user ID

    # ── Content ──
    title:      str            = ""            # Note title (optional)
    content:    str            = ""            # Note body text

    # ── Metadata ──
    status:     str = NoteStatus.ACTIVE.value  # active | deleted
    tags:       List[str] = field(
        default_factory=list
    )                                           # Optional tags

    # ── Timestamps ──
    created_at: datetime = field(
        default_factory=utcnow_naive
    )
    updated_at: datetime = field(
        default_factory=utcnow_naive
    )
    deleted_at: Optional[datetime] = None      # Set when soft-deleted

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        """Convert to MongoDB-compatible dictionary."""
        return {
            "note_id":    self.note_id,
            "user_id":    self.user_id,
            "title":      self.title,
            "content":    self.content,
            "status":     self.status,
            "tags":       self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NoteModel":
        """Reconstruct NoteModel from a MongoDB document."""
        return cls(
            note_id=    data.get("note_id", ""),
            user_id=    data.get("user_id", 0),
            title=      data.get("title", ""),
            content=    data.get("content", ""),
            status=     data.get("status", NoteStatus.ACTIVE.value),
            tags=       data.get("tags", []),
            created_at= data.get("created_at", utcnow_naive()),
            updated_at= data.get("updated_at", utcnow_naive()),
            deleted_at= data.get("deleted_at"),
        )

    # ================================================================
    #   COMPUTED PROPERTIES
    # ================================================================

    @property
    def is_active(self) -> bool:
        """True if note is not deleted."""
        return self.status == NoteStatus.ACTIVE.value

    @property
    def short_content(self) -> str:
        """Return first 100 chars of content for previews."""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."

    @property
    def display_title(self) -> str:
        """Return title or fallback to content preview."""
        return self.title if self.title else f"Note #{self.note_id[:8]}"

    def __repr__(self) -> str:
        return (
            f"NoteModel(id={self.note_id[:8]}, "
            f"user={self.user_id}, "
            f"title={self.display_title!r})"
        )


# ============================================================
#   AI CONTEXT MODEL
#   Stores per-user conversation history for AI memory
# ============================================================

@dataclass
class AIContextMessage:
    """A single message in the AI conversation history."""
    role:      str    # "user" or "assistant"
    content:   str    # Message text
    timestamp: datetime = field(default_factory=utcnow_naive)

    def to_dict(self) -> dict:
        return {
            "role":      self.role,
            "content":   self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIContextMessage":
        return cls(
            role=      data.get("role", "user"),
            content=   data.get("content", ""),
            timestamp= data.get("timestamp", utcnow_naive()),
        )

    def to_openai_format(self) -> dict:
        """Convert to OpenAI API message format."""
        return {
            "role":    self.role,
            "content": self.content,
        }


@dataclass
class AIContextModel:
    """
    Stores a user's AI conversation context in the 'ai_context' collection.

    Has a TTL index — automatically deleted after AI_CONTEXT_EXPIRY seconds
    of inactivity, keeping the database clean.
    """

    # ── Identity ──
    user_id:    int                             # Telegram user ID (unique)

    # ── Conversation History ──
    messages:   List[AIContextMessage] = field(
        default_factory=list
    )

    # ── Metadata ──
    total_tokens_used: int      = 0            # Running token count
    total_requests:    int      = 0            # Total AI requests made

    # ── Timestamps ──
    created_at: datetime = field(default_factory=utcnow_naive)
    updated_at: datetime = field(default_factory=utcnow_naive)  # TTL based on this

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        """Convert to MongoDB-compatible dictionary."""
        return {
            "user_id":           self.user_id,
            "messages":          [m.to_dict() for m in self.messages],
            "total_tokens_used": self.total_tokens_used,
            "total_requests":    self.total_requests,
            "created_at":        self.created_at,
            "updated_at":        self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIContextModel":
        """Reconstruct AIContextModel from a MongoDB document."""
        messages = [
            AIContextMessage.from_dict(m)
            for m in data.get("messages", [])
        ]
        return cls(
            user_id=           data.get("user_id", 0),
            messages=          messages,
            total_tokens_used= data.get("total_tokens_used", 0),
            total_requests=    data.get("total_requests", 0),
            created_at=        data.get("created_at", utcnow_naive()),
            updated_at=        data.get("updated_at", utcnow_naive()),
        )

    # ================================================================
    #   CONTEXT MANAGEMENT
    # ================================================================

    def add_message(
        self,
        role: str,
        content: str,
        max_messages: int = 20,
    ) -> None:
        """
        Add a message to the context, trimming old ones if needed.

        Args:
            role:         "user" or "assistant"
            content:      Message text
            max_messages: Max messages to keep (sliding window)
        """
        self.messages.append(
            AIContextMessage(role=role, content=content)
        )

        # Trim to max size — keep most recent messages
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

        self.updated_at = utcnow_naive()

    def get_openai_messages(self) -> List[dict]:
        """
        Return messages in OpenAI API format.
        Excludes timestamps — only role + content.
        """
        return [m.to_openai_format() for m in self.messages]

    def clear(self) -> None:
        """Clear all messages from context."""
        self.messages = []
        self.updated_at = utcnow_naive()

    @property
    def message_count(self) -> int:
        """Number of messages in current context."""
        return len(self.messages)

    def __repr__(self) -> str:
        return (
            f"AIContextModel(user={self.user_id}, "
            f"messages={self.message_count}, "
            f"tokens={self.total_tokens_used})"
        )


# ============================================================
#   ADMIN LOG MODEL
#   Records all admin actions for audit trail
# ============================================================

@dataclass
class AdminLogModel:
    """
    Records every admin action in the 'admin_logs' collection.
    Provides full audit trail for accountability.
    """

    # ── Identity ──
    log_id:     str                             # UUID string
    admin_id:   int                             # Admin's Telegram user ID
    action:     str                             # Action performed (AdminAction enum)

    # ── Details ──
    target_id:  Optional[int]  = None          # Target user ID (if applicable)
    details:    Dict[str, Any] = field(
        default_factory=dict
    )                                           # Action-specific metadata
    result:     str = "success"                # success | failure
    error_msg:  Optional[str] = None           # Error message if failed

    # ── Timestamps ──
    created_at: datetime = field(default_factory=utcnow_naive)

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        return {
            "log_id":    self.log_id,
            "admin_id":  self.admin_id,
            "action":    self.action,
            "target_id": self.target_id,
            "details":   self.details,
            "result":    self.result,
            "error_msg": self.error_msg,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AdminLogModel":
        return cls(
            log_id=     data.get("log_id", ""),
            admin_id=   data.get("admin_id", 0),
            action=     data.get("action", ""),
            target_id=  data.get("target_id"),
            details=    data.get("details", {}),
            result=     data.get("result", "success"),
            error_msg=  data.get("error_msg"),
            created_at= data.get("created_at", utcnow_naive()),
        )

    def __repr__(self) -> str:
        return (
            f"AdminLogModel(admin={self.admin_id}, "
            f"action={self.action}, "
            f"result={self.result})"
        )


# ============================================================
#   BROADCAST MODEL
#   Records every broadcast message sent by admins
# ============================================================

@dataclass
class BroadcastModel:
    """
    Records broadcast messages in the 'broadcasts' collection.
    Tracks delivery stats for each broadcast.
    """

    # ── Identity ──
    broadcast_id: str                          # UUID string
    admin_id:     int                          # Sending admin's ID

    # ── Content ──
    message_text: str      = ""               # Broadcast text
    has_media:    bool     = False            # Has photo/video/doc
    media_type:   Optional[str] = None        # photo | video | document

    # ── Delivery Stats ──
    total_users:  int = 0                     # Total users targeted
    sent_count:   int = 0                     # Successfully sent
    failed_count: int = 0                     # Failed deliveries
    status:       str = "pending"             # pending | sending | done | failed

    # ── Timestamps ──
    created_at:   datetime = field(default_factory=utcnow_naive)
    completed_at: Optional[datetime] = None   # When broadcast finished

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        return {
            "broadcast_id": self.broadcast_id,
            "admin_id":     self.admin_id,
            "message_text": self.message_text,
            "has_media":    self.has_media,
            "media_type":   self.media_type,
            "total_users":  self.total_users,
            "sent_count":   self.sent_count,
            "failed_count": self.failed_count,
            "status":       self.status,
            "created_at":   self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BroadcastModel":
        return cls(
            broadcast_id= data.get("broadcast_id", ""),
            admin_id=     data.get("admin_id", 0),
            message_text= data.get("message_text", ""),
            has_media=    data.get("has_media", False),
            media_type=   data.get("media_type"),
            total_users=  data.get("total_users", 0),
            sent_count=   data.get("sent_count", 0),
            failed_count= data.get("failed_count", 0),
            status=       data.get("status", "pending"),
            created_at=   data.get("created_at", utcnow_naive()),
            completed_at= data.get("completed_at"),
        )

    @property
    def success_rate(self) -> float:
        """Return delivery success rate as percentage."""
        if self.total_users == 0:
            return 0.0
        return round((self.sent_count / self.total_users) * 100, 1)

    def __repr__(self) -> str:
        return (
            f"BroadcastModel(id={self.broadcast_id[:8]}, "
            f"admin={self.admin_id}, "
            f"sent={self.sent_count}/{self.total_users})"
        )


# ============================================================
#   API STATS MODEL
#   Tracks OpenAI API usage per user per day
# ============================================================

@dataclass
class APIStatsModel:
    """
    Tracks OpenAI API usage in the 'api_stats' collection.
    One document per user per day.
    """

    # ── Identity ──
    user_id:        int                        # Telegram user ID
    date:           str                        # YYYY-MM-DD format

    # ── Usage Counts ──
    requests_count: int = 0                    # API calls made today
    tokens_used:    int = 0                    # Total tokens consumed
    prompt_tokens:  int = 0                    # Prompt tokens
    completion_tokens: int = 0                 # Completion tokens

    # ── Cost Tracking (approximate) ──
    estimated_cost_usd: float = 0.0           # Approximate USD cost

    # ── Timestamps ──
    created_at: datetime = field(default_factory=utcnow_naive)
    updated_at: datetime = field(default_factory=utcnow_naive)

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        return {
            "user_id":             self.user_id,
            "date":                self.date,
            "requests_count":      self.requests_count,
            "tokens_used":         self.tokens_used,
            "prompt_tokens":       self.prompt_tokens,
            "completion_tokens":   self.completion_tokens,
            "estimated_cost_usd":  self.estimated_cost_usd,
            "created_at":          self.created_at,
            "updated_at":          self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "APIStatsModel":
        return cls(
            user_id=             data.get("user_id", 0),
            date=                data.get("date", ""),
            requests_count=      data.get("requests_count", 0),
            tokens_used=         data.get("tokens_used", 0),
            prompt_tokens=       data.get("prompt_tokens", 0),
            completion_tokens=   data.get("completion_tokens", 0),
            estimated_cost_usd=  data.get("estimated_cost_usd", 0.0),
            created_at=          data.get("created_at", utcnow_naive()),
            updated_at=          data.get("updated_at", utcnow_naive()),
        )

    def __repr__(self) -> str:
        return (
            f"APIStatsModel(user={self.user_id}, "
            f"date={self.date}, "
            f"requests={self.requests_count}, "
            f"tokens={self.tokens_used})"
        )


# ============================================================
#   RATE LIMIT MODEL
#   Tracks per-user rate limit windows
# ============================================================

@dataclass
class RateLimitModel:
    """
    Tracks rate limit counters per user per window.
    Stored in 'rate_limits' collection with TTL index.
    """

    # ── Identity ──
    user_id:    int                            # Telegram user ID
    window:     str                            # Window key: "msg:60" | "ai:3600"

    # ── Counters ──
    count:      int      = 0                   # Requests in this window
    limit:      int      = 10                  # Max allowed

    # ── Timestamps ──
    window_start: datetime = field(default_factory=utcnow_naive)
    expires_at:   datetime = field(default_factory=utcnow_naive)  # TTL field
    updated_at:   datetime = field(default_factory=utcnow_naive)

    # ================================================================
    #   SERIALIZATION
    # ================================================================

    def to_dict(self) -> dict:
        return {
            "user_id":      self.user_id,
            "window":       self.window,
            "count":        self.count,
            "limit":        self.limit,
            "window_start": self.window_start,
            "expires_at":   self.expires_at,
            "updated_at":   self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RateLimitModel":
        return cls(
            user_id=      data.get("user_id", 0),
            window=       data.get("window", ""),
            count=        data.get("count", 0),
            limit=        data.get("limit", 10),
            window_start= data.get("window_start", utcnow_naive()),
            expires_at=   data.get("expires_at", utcnow_naive()),
            updated_at=   data.get("updated_at", utcnow_naive()),
        )

    @property
    def is_exceeded(self) -> bool:
        """True if rate limit has been exceeded."""
        return self.count >= self.limit

    @property
    def remaining(self) -> int:
        """Remaining requests in this window."""
        return max(0, self.limit - self.count)

    def __repr__(self) -> str:
        return (
            f"RateLimitModel(user={self.user_id}, "
            f"window={self.window}, "
            f"count={self.count}/{self.limit})"
        )
