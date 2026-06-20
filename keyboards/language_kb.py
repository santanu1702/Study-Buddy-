# ============================================================
#         StudyBuddyV3BOT — Language Keyboard
#         Language selection and confirmation keyboards
#         Supports all 4 bot languages with visual indicators
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import Language, EmojiConstants


# ============================================================
#   LANGUAGE KEYBOARD
# ============================================================

class LanguageKeyboard:
    """
    Builds all language selection inline keyboards.

    Keyboards:
    - language_selection: Full language picker with current highlighted
    - after_selection:    Confirmation buttons after language change
    - quick_switch:       Compact language switcher for inline use
    """

    # ================================================================
    #   LANGUAGE SELECTION
    # ================================================================

    @staticmethod
    def language_selection(
        current_lang: str = "en",
    ) -> InlineKeyboardMarkup:
        """
        Build the full language selection keyboard.
        Highlights currently active language with a checkmark.

        Args:
            current_lang: Currently active language code
        """

        def lang_btn(
            code:  str,
            flag:  str,
            name:  str,
        ) -> InlineKeyboardButton:
            """Build a language button with active indicator."""
            is_active = code == current_lang
            label     = (
                f"✅ {flag} {name}"
                if is_active
                else f"{flag} {name}"
            )
            return InlineKeyboardButton(
                text=          label,
                callback_data= f"lang:set:{code}",
            )

        buttons = [

            # ── Row 1: English ──
            [
                lang_btn("en", "🇬🇧", "English"),
            ],

            # ── Row 2: Hindi ──
            [
                lang_btn("hi", "🇮🇳", "हिंदी (Hindi)"),
            ],

            # ── Row 3: Bengali ──
            [
                lang_btn("bn", "🇧🇩", "বাংলা (Bengali)"),
            ],

            # ── Row 4: Arabic ──
            [
                lang_btn("ar", "🇸🇦", "العربية (Arabic)"),
            ],

            # ── Row 5: Back to menu ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "lang:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   AFTER SELECTION
    # ================================================================

    @staticmethod
    def after_selection(
        lang_code: str = "en",
    ) -> InlineKeyboardMarkup:
        """
        Build confirmation keyboard shown after language change.
        Offers to go back to menu or change again.

        Args:
            lang_code: Newly selected language code
        """
        buttons = [

            # ── Row 1: Go to main menu ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.ROCKET} Main Menu",
                    callback_data= "menu:main",
                ),
            ],

            # ── Row 2: Change language again ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.LANGUAGE} Change Language",
                    callback_data= "lang:open",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   QUICK SWITCH
    # ================================================================

    @staticmethod
    def quick_switch(
        current_lang: str = "en",
    ) -> InlineKeyboardMarkup:
        """
        Build a compact 2x2 language switcher.
        Used in settings or quick-access panels.

        Args:
            current_lang: Currently active language code
        """

        def btn(code: str, flag: str) -> InlineKeyboardButton:
            is_active = code == current_lang
            label     = f"✅ {flag}" if is_active else flag
            return InlineKeyboardButton(
                text=          label,
                callback_data= f"lang:set:{code}",
            )

        buttons = [
            # Row 1: EN + HI
            [
                btn("en", "🇬🇧 EN"),
                btn("hi", "🇮🇳 HI"),
            ],
            # Row 2: BN + AR
            [
                btn("bn", "🇧🇩 BN"),
                btn("ar", "🇸🇦 AR"),
            ],
            # Row 3: Back
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Back",
                    callback_data= "lang:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   LANGUAGE INFO
    # ================================================================

    @staticmethod
    def get_language_flag(lang_code: str) -> str:
        """
        Return flag emoji for a language code.

        Args:
            lang_code: Language code (en, hi, bn, ar)

        Returns:
            Flag emoji string
        """
        flags = {
            "en": "🇬🇧",
            "hi": "🇮🇳",
            "bn": "🇧🇩",
            "ar": "🇸🇦",
        }
        return flags.get(lang_code, "🌐")

    @staticmethod
    def get_language_name(lang_code: str) -> str:
        """
        Return display name for a language code.

        Args:
            lang_code: Language code

        Returns:
            Human-readable language name
        """
        names = {
            "en": "English",
            "hi": "हिंदी",
            "bn": "বাংলা",
            "ar": "العربية",
        }
        return names.get(lang_code, lang_code.upper())