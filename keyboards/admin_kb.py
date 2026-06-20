# ============================================================
#         StudyBuddyV3BOT — Admin Keyboard
#         All inline keyboards for the admin panel
#         Secure, clean, fast navigation UI
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EmojiConstants, AdminAction


# ============================================================
#   ADMIN KEYBOARD
# ============================================================

class AdminKeyboard:
    """
    Builds all inline keyboards for the admin panel.

    Keyboards:
    - main_panel:        Primary admin dashboard navigation
    - user_management:   Ban/unban/list users
    - broadcast_confirm: Confirm before sending broadcast
    - logs_panel:        Log viewer actions
    - back_button:       Single back to admin panel button
    - cancel_action:     Single cancel current action button
    """

    # ================================================================
    #   MAIN PANEL
    # ================================================================

    @staticmethod
    def main_panel(
        maintenance_on: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Build the main admin panel keyboard.
        Full feature navigation in a clean grid layout.

        Args:
            maintenance_on: Current maintenance mode state
                           Determines toggle button label
        """

        # Maintenance toggle button
        if maintenance_on:
            maintenance_btn = InlineKeyboardButton(
                text=          f"🟢 Disable Maintenance",
                callback_data= f"admin:{AdminAction.MAINTENANCE_OFF}",
            )
        else:
            maintenance_btn = InlineKeyboardButton(
                text=          f"🔴 Enable Maintenance",
                callback_data= f"admin:{AdminAction.MAINTENANCE_ON}",
            )

        buttons = [

            # ── Row 1: Stats ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.USERS} Total Users",
                    callback_data= f"admin:{AdminAction.TOTAL_USERS}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.STATS} Active Users",
                    callback_data= f"admin:{AdminAction.ACTIVE_USERS}",
                ),
            ],

            # ── Row 2: User Management ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BAN} Ban User",
                    callback_data= f"admin:{AdminAction.BAN_USER}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.UNBAN} Unban User",
                    callback_data= f"admin:{AdminAction.UNBAN_USER}",
                ),
            ],

            # ── Row 3: Banned list + Broadcast ──
            [
                InlineKeyboardButton(
                    text=          f"📋 Banned List",
                    callback_data= f"admin:{AdminAction.LIST_BANNED}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BROADCAST} Broadcast",
                    callback_data= f"admin:{AdminAction.BROADCAST}",
                ),
            ],

            # ── Row 4: API Stats + Logs ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.STATS} API Stats",
                    callback_data= f"admin:{AdminAction.API_STATS}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.LOGS} View Logs",
                    callback_data= f"admin:{AdminAction.VIEW_LOGS}",
                ),
            ],

            # ── Row 5: Maintenance toggle ──
            [
                maintenance_btn,
            ],

            # ── Row 6: Refresh ──
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.REFRESH} Refresh",
                    callback_data= f"admin:{AdminAction.REFRESH}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   BROADCAST CONFIRM
    # ================================================================

    @staticmethod
    def broadcast_confirm() -> InlineKeyboardMarkup:
        """
        Build broadcast confirmation keyboard.
        Shown after admin inputs broadcast message.
        Two clear options: confirm send or cancel.
        """
        buttons = [
            # Row 1: Confirm (prominent)
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BROADCAST} Yes, Send Broadcast",
                    callback_data= f"admin:{AdminAction.BROADCAST_CONFIRM}",
                ),
            ],
            # Row 2: Cancel (safe exit)
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel Broadcast",
                    callback_data= f"admin:{AdminAction.BROADCAST_CANCEL}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   LOGS PANEL
    # ================================================================

    @staticmethod
    def logs_panel() -> InlineKeyboardMarkup:
        """
        Build the logs viewer action keyboard.
        Options to clear old logs or go back.
        """
        buttons = [
            # Row 1: Clear old logs
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Clear Old Logs (30d)",
                    callback_data= f"admin:{AdminAction.CLEAR_LOGS}",
                ),
            ],
            # Row 2: Back to panel
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Admin Panel",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   USER MANAGEMENT
    # ================================================================

    @staticmethod
    def user_management() -> InlineKeyboardMarkup:
        """
        Build user management keyboard.
        Quick access to all user control actions.
        """
        buttons = [
            # Row 1: Ban + Unban
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BAN} Ban User",
                    callback_data= f"admin:{AdminAction.BAN_USER}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.UNBAN} Unban User",
                    callback_data= f"admin:{AdminAction.UNBAN_USER}",
                ),
            ],
            # Row 2: List banned
            [
                InlineKeyboardButton(
                    text=          f"📋 View Banned List",
                    callback_data= f"admin:{AdminAction.LIST_BANNED}",
                ),
            ],
            # Row 3: Back
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Admin Panel",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   UTILITY KEYBOARDS
    # ================================================================

    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Single back to admin panel button."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Admin Panel",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ]
        ])

    @staticmethod
    def cancel_action() -> InlineKeyboardMarkup:
        """
        Single cancel button for admin input states.
        Returns to admin panel on press.
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ]
        ])

    @staticmethod
    def confirm_dangerous_action(
        confirm_data: str,
        action_label: str = "Yes, Proceed",
    ) -> InlineKeyboardMarkup:
        """
        Build a confirmation keyboard for dangerous admin actions.
        Extra prominent cancel button to prevent accidents.

        Args:
            confirm_data: Callback data for the confirm button
            action_label: Label for the confirm button
        """
        buttons = [
            # Row 1: Confirm (dangerous action)
            [
                InlineKeyboardButton(
                    text=          f"⚠️ {action_label}",
                    callback_data= confirm_data,
                ),
            ],
            # Row 2: Cancel (safe)
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel — Go Back",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def refresh_button() -> InlineKeyboardMarkup:
        """Single refresh button for data views."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.REFRESH} Refresh",
                    callback_data= f"admin:{AdminAction.REFRESH}",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Panel",
                    callback_data= f"admin:{AdminAction.BACK_TO_PANEL}",
                ),
            ]
        ])