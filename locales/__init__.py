# ============================================================
#         StudyBuddyV3BOT — Locales Package Init
#         Exposes i18n engine and language string modules
#         at package level for clean imports
# ============================================================

from locales.translator import (
    get_text,
    set_user_language,
    get_user_language,
    detect_language,
)

from locales import en, hi, bn, ar

__all__ = [
    # ── i18n Engine ──
    "get_text",           # Get translated string by key
    "set_user_language",  # Set language for a user
    "get_user_language",  # Get current language for a user
    "detect_language",    # Auto-detect language from text

    # ── Language Modules ──
    "en",                 # English strings
    "hi",                 # Hindi strings
    "bn",                 # Bengali strings
    "ar",                 # Arabic strings
]