# ============================================================
#         StudyBuddyV3BOT — Translator Keyboard
#         All inline keyboards for the translation feature
#         Language picker + action buttons
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EmojiConstants


# ============================================================
#   TRANSLATOR KEYBOARD
# ============================================================

class TranslatorKeyboard:
    """
    Builds all inline keyboards for the translator feature.

    Keyboards:
    - translator_menu:   Main translator entry menu
    - language_picker:   Full language selection grid
    - after_translation: Buttons shown after translation result
    - cancel_button:     Single cancel button
    - retry_button:      Retry after translation error
    """

    # ================================================================
    #   TRANSLATOR MENU
    # ================================================================

    @staticmethod
    def translator_menu() -> InlineKeyboardMarkup:
        """
        Build the main translator menu keyboard.
        Entry point for the translation feature.
        """
        buttons = [
            # Row 1: Start translation
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.TRANSLATOR} Translate Text",
                    callback_data= "trans:start",
                ),
            ],
            # Row 2: Back to main menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "trans:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   LANGUAGE PICKER
    # ================================================================

    @staticmethod
    def language_picker() -> InlineKeyboardMarkup:
        """
        Build the full language selection keyboard.
        Shows most popular languages as quick buttons.
        Organized by region for easy navigation.
        """
        buttons = [

            # ── Section: South Asian ──
            [
                InlineKeyboardButton(
                    text=          "🇮🇳 Hindi",
                    callback_data= "trans:lang:hi",
                ),
                InlineKeyboardButton(
                    text=          "🇧🇩 Bengali",
                    callback_data= "trans:lang:bn",
                ),
                InlineKeyboardButton(
                    text=          "🇵🇰 Urdu",
                    callback_data= "trans:lang:ur",
                ),
            ],

            # ── Section: East Asian ──
            [
                InlineKeyboardButton(
                    text=          "🇨🇳 Chinese",
                    callback_data= "trans:lang:zh-CN",
                ),
                InlineKeyboardButton(
                    text=          "🇯🇵 Japanese",
                    callback_data= "trans:lang:ja",
                ),
                InlineKeyboardButton(
                    text=          "🇰🇷 Korean",
                    callback_data= "trans:lang:ko",
                ),
            ],

            # ── Section: Middle East ──
            [
                InlineKeyboardButton(
                    text=          "🇸🇦 Arabic",
                    callback_data= "trans:lang:ar",
                ),
                InlineKeyboardButton(
                    text=          "🇮🇷 Persian",
                    callback_data= "trans:lang:fa",
                ),
                InlineKeyboardButton(
                    text=          "🇹🇷 Turkish",
                    callback_data= "trans:lang:tr",
                ),
            ],

            # ── Section: European ──
            [
                InlineKeyboardButton(
                    text=          "🇬🇧 English",
                    callback_data= "trans:lang:en",
                ),
                InlineKeyboardButton(
                    text=          "🇫🇷 French",
                    callback_data= "trans:lang:fr",
                ),
                InlineKeyboardButton(
                    text=          "🇩🇪 German",
                    callback_data= "trans:lang:de",
                ),
            ],

            # ── Section: European 2 ──
            [
                InlineKeyboardButton(
                    text=          "🇪🇸 Spanish",
                    callback_data= "trans:lang:es",
                ),
                InlineKeyboardButton(
                    text=          "🇮🇹 Italian",
                    callback_data= "trans:lang:it",
                ),
                InlineKeyboardButton(
                    text=          "🇵🇹 Portuguese",
                    callback_data= "trans:lang:pt",
                ),
            ],

            # ── Section: Eastern European ──
            [
                InlineKeyboardButton(
                    text=          "🇷🇺 Russian",
                    callback_data= "trans:lang:ru",
                ),
                InlineKeyboardButton(
                    text=          "🇺🇦 Ukrainian",
                    callback_data= "trans:lang:uk",
                ),
                InlineKeyboardButton(
                    text=          "🇵🇱 Polish",
                    callback_data= "trans:lang:pl",
                ),
            ],

            # ── Section: Southeast Asian ──
            [
                InlineKeyboardButton(
                    text=          "🇮🇩 Indonesian",
                    callback_data= "trans:lang:id",
                ),
                InlineKeyboardButton(
                    text=          "🇻🇳 Vietnamese",
                    callback_data= "trans:lang:vi",
                ),
                InlineKeyboardButton(
                    text=          "🇹🇭 Thai",
                    callback_data= "trans:lang:th",
                ),
            ],

            # ── Section: African ──
            [
                InlineKeyboardButton(
                    text=          "🇳🇬 Yoruba",
                    callback_data= "trans:lang:yo",
                ),
                InlineKeyboardButton(
                    text=          "🇰🇪 Swahili",
                    callback_data= "trans:lang:sw",
                ),
                InlineKeyboardButton(
                    text=          "🇿🇦 Afrikaans",
                    callback_data= "trans:lang:af",
                ),
            ],

            # ── Custom language ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.GLOBE} Other Language...",
                    callback_data= "trans:custom",
                ),
            ],

            # ── Cancel ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= "trans:clear",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   AFTER TRANSLATION
    # ================================================================

    @staticmethod
    def after_translation() -> InlineKeyboardMarkup:
        """
        Build keyboard shown after a successful translation.
        Allows translating same text to another language
        or starting fresh.
        """
        buttons = [
            # Row 1: Translate again to different language
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.REFRESH} Translate Again",
                    callback_data= "trans:again",
                ),
            ],
            # Row 2: New translation + Main menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.TRANSLATOR} New Text",
                    callback_data= "trans:start",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Menu",
                    callback_data= "trans:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   UTILITY KEYBOARDS
    # ================================================================

    @staticmethod
    def cancel_button() -> InlineKeyboardMarkup:
        """Single cancel button — used during text input state."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= "trans:clear",
                ),
            ]
        ])

    @staticmethod
    def retry_button() -> InlineKeyboardMarkup:
        """
        Build retry keyboard shown after a translation error.
        Offers retry with language picker or start over.
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.REFRESH} Try Again",
                    callback_data= "trans:again",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.TRANSLATOR} New Text",
                    callback_data= "trans:start",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "trans:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Single back to translator menu button."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Translator Menu",
                    callback_data= "trans:open",
                ),
            ]
        ])