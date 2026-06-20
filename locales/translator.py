# ============================================================
#         StudyBuddyV3BOT — i18n Engine
#         Central translation system
#         Loads strings from language modules
#         Supports variable substitution
# ============================================================

from typing import Optional, Dict, Any
from config.constants import Language
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ============================================================
#   LAZY LOAD LANGUAGE MODULES
#   Loaded on first use — not at import time
# ============================================================

_LANGUAGE_MODULES: Dict[str, Any] = {}


def _load_language(lang_code: str) -> Dict[str, str]:
    """
    Lazily load a language module by code.
    Caches loaded modules in _LANGUAGE_MODULES.

    Args:
        lang_code: Language code (en, hi, bn, ar)

    Returns:
        Dict of string keys to translated strings
    """
    if lang_code in _LANGUAGE_MODULES:
        return _LANGUAGE_MODULES[lang_code]

    try:
        if lang_code == "en":
            from locales import en
            _LANGUAGE_MODULES["en"] = en.STRINGS
        elif lang_code == "hi":
            from locales import hi
            _LANGUAGE_MODULES["hi"] = hi.STRINGS
        elif lang_code == "bn":
            from locales import bn
            _LANGUAGE_MODULES["bn"] = bn.STRINGS
        elif lang_code == "ar":
            from locales import ar
            _LANGUAGE_MODULES["ar"] = ar.STRINGS
        else:
            # Fallback to English for unsupported languages
            from locales import en
            _LANGUAGE_MODULES[lang_code] = en.STRINGS

        return _LANGUAGE_MODULES[lang_code]

    except ImportError as e:
        logger.error(f"Failed to load language module '{lang_code}': {e}")
        # Ultimate fallback — load English
        try:
            from locales import en
            _LANGUAGE_MODULES[lang_code] = en.STRINGS
            return en.STRINGS
        except Exception:
            return {}


# ============================================================
#   CORE i18n FUNCTIONS
# ============================================================

def get_text(
    key:      str,
    lang:     Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Get a translated string by key for the given language.

    Supports variable substitution via kwargs.
    Falls back to English if key not found in target language.
    Falls back to key name if not found anywhere.

    Args:
        key:    String key (e.g. "welcome", "ai_error")
        lang:   Language code (default: settings.DEFAULT_LANGUAGE)
        **kwargs: Variables to substitute in the string
                  e.g. get_text("welcome_back", lang="hi", name="John")

    Returns:
        Translated and formatted string

    Usage:
        text = get_text("welcome", lang="hi")
        text = get_text("ai_rate_limited", lang="en",
                        wait_time=60, limit=20)
    """
    # Use default language if none specified
    if not lang:
        lang = settings.DEFAULT_LANGUAGE

    # Normalize language code
    lang = lang.lower().strip()

    # Validate language code
    valid_codes = Language.choices()
    if lang not in valid_codes:
        lang = settings.DEFAULT_LANGUAGE

    # Load language strings
    strings = _load_language(lang)

    # Get the string
    text = strings.get(key)

    # Fallback to English if not found in target language
    if text is None and lang != "en":
        logger.debug(
            f"Key '{key}' not found in '{lang}', "
            f"falling back to English"
        )
        en_strings = _load_language("en")
        text        = en_strings.get(key)

    # Final fallback — return key name
    if text is None:
        logger.warning(
            f"Translation key '{key}' not found in any language"
        )
        return key

    # Apply variable substitution
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            logger.warning(
                f"Missing variable {e} in translation key '{key}'"
            )
        except Exception as e:
            logger.warning(
                f"Error formatting translation key '{key}': {e}"
            )

    return text


def get_text_safe(
    key:      str,
    lang:     Optional[str] = None,
    default:  str           = "",
    **kwargs: Any,
) -> str:
    """
    Safe version of get_text that never raises exceptions.
    Returns default string if anything fails.

    Args:
        key:     String key
        lang:    Language code
        default: Default value if key not found
        **kwargs: Substitution variables

    Returns:
        Translated string or default
    """
    try:
        result = get_text(key, lang=lang, **kwargs)
        return result if result != key else default
    except Exception as e:
        logger.error(f"get_text_safe error for key '{key}': {e}")
        return default


def get_all_texts(lang: str) -> Dict[str, str]:
    """
    Get all strings for a language.
    Used for debugging or bulk operations.

    Args:
        lang: Language code

    Returns:
        Full dict of all translated strings
    """
    return _load_language(lang)


# ============================================================
#   USER LANGUAGE MANAGEMENT
#   In-memory store for active user language preferences
#   (session-level — DB is the persistent store)
# ============================================================

# In-memory language cache: {user_id: lang_code}
_user_languages: Dict[int, str] = {}


def set_user_language(user_id: int, lang_code: str) -> None:
    """
    Set language preference for a user in memory.
    Called when user changes language.

    Args:
        user_id:   Telegram user ID
        lang_code: Language code to set
    """
    valid_codes = Language.choices()
    if lang_code not in valid_codes:
        logger.warning(
            f"Invalid language code '{lang_code}' for user {user_id}, "
            f"using default '{settings.DEFAULT_LANGUAGE}'"
        )
        lang_code = settings.DEFAULT_LANGUAGE

    _user_languages[user_id] = lang_code
    logger.debug(
        f"Language set | User: {user_id} | Lang: {lang_code}"
    )


def get_user_language(user_id: int) -> str:
    """
    Get language preference for a user from memory.
    Falls back to DEFAULT_LANGUAGE if not set.

    Args:
        user_id: Telegram user ID

    Returns:
        Language code string
    """
    return _user_languages.get(user_id, settings.DEFAULT_LANGUAGE)


def clear_user_language(user_id: int) -> None:
    """
    Remove user's language from memory cache.
    Called on user deletion or session reset.

    Args:
        user_id: Telegram user ID
    """
    _user_languages.pop(user_id, None)


def get_user_text(
    user_id:  int,
    key:      str,
    **kwargs: Any,
) -> str:
    """
    Convenience function — get translated text for a user
    using their stored language preference.

    Args:
        user_id:  Telegram user ID
        key:      String key
        **kwargs: Substitution variables

    Returns:
        Translated string in user's language

    Usage:
        text = get_user_text(user_id, "welcome_back", name="John")
    """
    lang = get_user_language(user_id)
    return get_text(key, lang=lang, **kwargs)


# ============================================================
#   LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:
    """
    Attempt to detect language from text content.
    Uses simple Unicode range detection for supported languages.
    Falls back to DEFAULT_LANGUAGE if detection fails.

    Args:
        text: Input text to analyze

    Returns:
        Detected language code
    """
    if not text or not text.strip():
        return settings.DEFAULT_LANGUAGE

    text = text.strip()

    # Count characters in each script range
    arabic_count   = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    bengali_count  = sum(1 for c in text if '\u0980' <= c <= '\u09FF')

    total = len(text)
    if total == 0:
        return settings.DEFAULT_LANGUAGE

    # Determine dominant script
    threshold = 0.3  # 30% of characters in a script = detected

    if arabic_count / total >= threshold:
        return Language.ARABIC.value

    if devanagari_count / total >= threshold:
        return Language.HINDI.value

    if bengali_count / total >= threshold:
        return Language.BENGALI.value

    # Default to English for Latin script and others
    return Language.ENGLISH.value


def get_language_display_name(lang_code: str) -> str:
    """
    Get the display name for a language code.

    Args:
        lang_code: Language code (en, hi, bn, ar)

    Returns:
        Human-readable language name with flag
    """
    display_names = Language.display_names()
    return display_names.get(lang_code, f"🌐 {lang_code.upper()}")


def is_rtl(lang_code: str) -> bool:
    """
    Check if a language is right-to-left.
    Used for UI adjustments if needed.

    Args:
        lang_code: Language code

    Returns:
        True if RTL language
    """
    rtl_languages = {"ar", "fa", "ur", "he"}
    return lang_code.lower() in rtl_languages


def get_supported_languages() -> Dict[str, str]:
    """
    Get all supported language codes with display names.

    Returns:
        Dict of {code: display_name}
    """
    return Language.display_names()