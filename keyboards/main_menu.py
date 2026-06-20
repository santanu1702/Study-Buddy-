# ============================================================
#         StudyBuddyV3BOT — Main Menu Keyboard
#         All main navigation inline keyboards
#         Central hub for feature access
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EmojiConstants, CallbackPrefix


# ============================================================
#   MAIN MENU KEYBOARD
# ============================================================

class MainMenuKeyboard:
    """
    Builds all main menu and navigation inline keyboards.

    Keyboards:
    - main_menu:          Primary feature selection grid
    - ai_menu:            AI assistant sub-menu
    - ai_response_buttons: Buttons shown after AI response
    - help_menu:          Help screen navigation
    - cancel_button:      Single cancel button
    - back_button:        Single back to menu button
    """

    # ================================================================
    #   MAIN MENU
    # ================================================================

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Build the primary main menu keyboard.
        2-column grid with all major features.
        """
        buttons = [
            # Row 1 — AI + Calculator
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.AI} AI Assistant",
                    callback_data= "menu:ai",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CALCULATOR} Calculator",
                    callback_data= "menu:calc",
                ),
            ],
            # Row 2 — Translator + Notes
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.TRANSLATOR} Translator",
                    callback_data= "menu:translator",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.NOTES} My Notes",
                    callback_data= "menu:notes",
                ),
            ],
            # Row 3 — Language + Help
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.LANGUAGE} Language",
                    callback_data= "menu:language",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.HELP} Help",
                    callback_data= "menu:help",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   AI MENU
    # ================================================================

    @staticmethod
    def ai_menu() -> InlineKeyboardMarkup:
        """
        Build the AI assistant sub-menu keyboard.
        Shown when user opens AI Assistant feature.
        """
        buttons = [
            # Row 1 — Ask question
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.AI} Ask a Question",
                    callback_data= "ai:ask",
                ),
            ],
            # Row 2 — Clear context
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Clear History",
                    callback_data= "ai:clear_context",
                ),
            ],
            # Row 3 — Back to main menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "menu:main",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def ai_response_buttons() -> InlineKeyboardMarkup:
        """
        Build action buttons shown after an AI response.
        Allows quick follow-up actions.
        """
        buttons = [
            # Row 1 — Ask another + Clear history
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.AI} Ask Another",
                    callback_data= "ai:ask",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Clear History",
                    callback_data= "ai:clear_context",
                ),
            ],
            # Row 2 — Back to menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "menu:main",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   HELP MENU
    # ================================================================

    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Build the help screen keyboard.
        Quick access to all features from help.
        """
        buttons = [
            # Row 1 — Feature shortcuts
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.AI} Try AI",
                    callback_data= "menu:ai",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CALCULATOR} Calculator",
                    callback_data= "menu:calc",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.TRANSLATOR} Translator",
                    callback_data= "menu:translator",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.NOTES} Notes",
                    callback_data= "menu:notes",
                ),
            ],
            # Row 3 — Back to main menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "menu:main",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   UTILITY KEYBOARDS
    # ================================================================

    @staticmethod
    def cancel_button(
        callback_data: str = "menu:cancel",
    ) -> InlineKeyboardMarkup:
        """
        Build a single cancel button.

        Args:
            callback_data: Custom callback (default: menu:cancel)
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= callback_data,
                ),
            ]
        ])

    @staticmethod
    def back_button(
        callback_data: str = "menu:main",
        label:         str = "Main Menu",
    ) -> InlineKeyboardMarkup:
        """
        Build a single back button.

        Args:
            callback_data: Custom callback (default: menu:main)
            label:         Button label text
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} {label}",
                    callback_data= callback_data,
                ),
            ]
        ])

    @staticmethod
    def back_and_cancel(
        back_data:   str = "menu:main",
        cancel_data: str = "menu:cancel",
    ) -> InlineKeyboardMarkup:
        """
        Build a row with both Back and Cancel buttons.

        Args:
            back_data:   Callback for back button
            cancel_data: Callback for cancel button
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Back",
                    callback_data= back_data,
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= cancel_data,
                ),
            ]
        ])

    @staticmethod
    def confirm_cancel(
        confirm_data: str,
        cancel_data:  str = "menu:main",
        confirm_label: str = "Yes, Confirm",
        cancel_label:  str = "Cancel",
    ) -> InlineKeyboardMarkup:
        """
        Build a confirm/cancel pair of buttons.
        Used for destructive actions needing confirmation.

        Args:
            confirm_data:  Callback for confirm button
            cancel_data:   Callback for cancel button
            confirm_label: Label for confirm button
            cancel_label:  Label for cancel button
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CONFIRM} {confirm_label}",
                    callback_data= confirm_data,
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} {cancel_label}",
                    callback_data= cancel_data,
                ),
            ]
        ])

    @staticmethod
    def main_menu_button() -> InlineKeyboardMarkup:
        """
        Single button that returns to main menu.
        Used at end of flows.
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.ROCKET} Main Menu",
                    callback_data= "menu:main",
                ),
            ]
        ])