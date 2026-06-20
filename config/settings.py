# ============================================================
#         StudyBuddyV3BOT — Settings (Pydantic v1 Compatible)
#         ✅ Works with pydantic==1.10.21
#         ✅ No field_validator, SecretStr, model_validator
# ============================================================

from pathlib import Path
from typing import List, Optional
from functools import lru_cache

# ✅ Pydantic v1 imports only
from pydantic import BaseSettings, Field, validator

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Central configuration class for StudyBuddyV3BOT.
    Pydantic v1 compatible — uses @validator not @field_validator.
    """

    # ================================================================
    #   🤖 TELEGRAM BOT
    # ================================================================
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")

    # ================================================================
    #   🗄️ MONGODB DATABASE
    # ================================================================
    MONGO_URI: str = Field(..., env="MONGO_URI")
    DB_NAME:   str = Field(default="studybuddy_db", env="DB_NAME")

    # ================================================================
    #   🧠 OPENAI
    # ================================================================
    OPENAI_API_KEY:     str   = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL:       str   = Field(default="gpt-4o-mini")
    OPENAI_MAX_TOKENS:  int   = Field(default=1000)
    OPENAI_TEMPERATURE: float = Field(default=0.7)

    # ================================================================
    #   👑 ADMIN
    # ================================================================
    ADMIN_IDS:    List[int] = Field(default=[])
    ADMIN_SECRET: str       = Field(default="studybuddy_admin_2024")

    # ================================================================
    #   🚦 RATE LIMITING
    # ================================================================
    RATE_LIMIT_MESSAGES:    int = Field(default=10)
    AI_RATE_LIMIT_PER_HOUR: int = Field(default=20)
    RATE_LIMIT_COOLDOWN:    int = Field(default=60)

    # ================================================================
    #   🌍 LANGUAGE
    # ================================================================
    DEFAULT_LANGUAGE: str = Field(default="en")

    # ================================================================
    #   ⚙️ BOT SETTINGS
    # ================================================================
    ENVIRONMENT:         str  = Field(default="production")
    MAINTENANCE_MODE:    bool = Field(default=False)
    MAINTENANCE_MESSAGE: str  = Field(
        default="Bot is under maintenance. Please try again later."
    )
    MAX_NOTES_PER_USER:  int  = Field(default=50)
    MAX_NOTE_LENGTH:     int  = Field(default=2000)

    # ================================================================
    #   📝 LOGGING
    # ================================================================
    LOG_LEVEL:        str = Field(default="INFO")
    LOG_FILE:         str = Field(default="logs/studybuddy.log")
    LOG_MAX_SIZE_MB:  int = Field(default=10)
    LOG_BACKUP_COUNT: int = Field(default=5)

    # ================================================================
    #   🔄 AI CONTEXT MEMORY
    # ================================================================
    AI_CONTEXT_MAX_MESSAGES: int = Field(default=20)
    AI_CONTEXT_EXPIRY:       int = Field(default=3600)

    # ================================================================
    #   📡 POLLING
    # ================================================================
    POLL_INTERVAL:        float = Field(default=1.0)
    POLL_TIMEOUT:         int   = Field(default=30)
    DROP_PENDING_UPDATES: bool  = Field(default=True)

    # ================================================================
    #   ✅ VALIDATORS — Pydantic v1 style (@validator)
    # ================================================================

    @validator("ADMIN_IDS", pre=True, always=True)
    def parse_admin_ids(cls, value):
        """Parse ADMIN_IDS from comma-separated string or list."""
        if isinstance(value, list):
            return [int(v) for v in value if str(v).strip()]
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                return [
                    int(i.strip())
                    for i in value.split(",")
                    if i.strip()
                ]
            except ValueError:
                return []
        if isinstance(value, int):
            return [value]
        return []

    @validator("LOG_LEVEL", pre=True, always=True)
    def validate_log_level(cls, v):
        """Ensure LOG_LEVEL is valid."""
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = str(v).upper().strip()
        return upper if upper in valid else "INFO"

    @validator("DEFAULT_LANGUAGE", pre=True, always=True)
    def validate_language(cls, v):
        """Ensure DEFAULT_LANGUAGE is supported."""
        supported = {"en", "hi", "bn", "ar"}
        lower = str(v).lower().strip()
        return lower if lower in supported else "en"

    @validator("ENVIRONMENT", pre=True, always=True)
    def validate_environment(cls, v):
        """Ensure ENVIRONMENT is valid."""
        valid = {"development", "production", "staging"}
        lower = str(v).lower().strip()
        return lower if lower in valid else "production"

    @validator("OPENAI_TEMPERATURE", pre=True, always=True)
    def validate_temperature(cls, v):
        """Clamp temperature between 0.0 and 1.0."""
        try:
            f = float(v)
            return max(0.0, min(1.0, f))
        except (ValueError, TypeError):
            return 0.7

    @validator("OPENAI_MAX_TOKENS", pre=True, always=True)
    def validate_max_tokens(cls, v):
        """Clamp max_tokens between 100 and 4096."""
        try:
            i = int(v)
            return max(100, min(4096, i))
        except (ValueError, TypeError):
            return 1000

    # ================================================================
    #   COMPUTED PROPERTIES
    # ================================================================

    @property
    def bot_token(self) -> str:
        """Return BOT_TOKEN as plain string."""
        return self.BOT_TOKEN

    @property
    def mongo_uri(self) -> str:
        """Return MONGO_URI as plain string."""
        return self.MONGO_URI

    @property
    def openai_api_key(self) -> str:
        """Return OPENAI_API_KEY as plain string."""
        return self.OPENAI_API_KEY

    @property
    def is_production(self) -> bool:
        """True if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """True if running in development."""
        return self.ENVIRONMENT == "development"

    @property
    def is_maintenance(self) -> bool:
        """True if maintenance mode is active."""
        return self.MAINTENANCE_MODE

    @property
    def log_file_path(self) -> Path:
        """Return absolute path to log file."""
        path = Path(self.LOG_FILE)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @property
    def log_max_bytes(self) -> int:
        """Return log max size in bytes."""
        return self.LOG_MAX_SIZE_MB * 1024 * 1024

    def is_admin(self, user_id: int) -> bool:
        """Check if a user ID is an admin."""
        return user_id in self.ADMIN_IDS

    def mask_sensitive(self) -> dict:
        """Return settings dict with secrets masked — safe for logging."""
        token_preview = (
            f"...{self.BOT_TOKEN[-6:]}"
            if len(self.BOT_TOKEN) > 6
            else "***"
        )
        key_preview = (
            f"sk-...{self.OPENAI_API_KEY[-4:]}"
            if len(self.OPENAI_API_KEY) > 4
            else "***"
        )
        return {
            "BOT_TOKEN":             token_preview,
            "MONGO_URI":             "***masked***",
            "OPENAI_API_KEY":        key_preview,
            "OPENAI_MODEL":          self.OPENAI_MODEL,
            "OPENAI_MAX_TOKENS":     self.OPENAI_MAX_TOKENS,
            "OPENAI_TEMPERATURE":    self.OPENAI_TEMPERATURE,
            "ADMIN_IDS":             self.ADMIN_IDS,
            "ENVIRONMENT":           self.ENVIRONMENT,
            "MAINTENANCE_MODE":      self.MAINTENANCE_MODE,
            "DEFAULT_LANGUAGE":      self.DEFAULT_LANGUAGE,
            "LOG_LEVEL":             self.LOG_LEVEL,
            "DB_NAME":               self.DB_NAME,
            "RATE_LIMIT_MESSAGES":   self.RATE_LIMIT_MESSAGES,
            "AI_RATE_LIMIT_PER_HOUR": self.AI_RATE_LIMIT_PER_HOUR,
            "POLL_INTERVAL":         self.POLL_INTERVAL,
            "DROP_PENDING_UPDATES":  self.DROP_PENDING_UPDATES,
        }

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"env={self.ENVIRONMENT}, "
            f"model={self.OPENAI_MODEL}, "
            f"admins={self.ADMIN_IDS}, "
            f"maintenance={self.MAINTENANCE_MODE}"
            f")"
        )

    # ================================================================
    #   PYDANTIC v1 CONFIG CLASS
    # ================================================================
    class Config:
        env_file          = ".env"
        env_file_encoding = "utf-8"
        case_sensitive    = False
        extra             = "ignore"


# ============================================================
#   SINGLETON INSTANCE
# ============================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()


settings: Settings = get_settings()
