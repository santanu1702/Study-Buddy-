# ============================================================
#         StudyBuddyV3BOT — Maintenance Middleware
#         Blocks all non-admin users during maintenance
#         Runs first — priority group -3
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from config.constants import EmojiConstants
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   MAINTENANCE MIDDLEWARE
# ============================================================

class MaintenanceMiddleware:
    """
    Maintenance mode gate middleware.

    Runs on every update BEFORE all other middlewares.
    When maintenance mode is ON:
    - Admins pass through freely
    - All other users receive maintenance message
    - Callback queries get alert popup
    - No DB operations performed

    Priority group: -3 (runs first of all middlewares)
    """

    async def process(
        self,
        update:  Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Main middleware processor.
        Checks maintenance mode on every incoming update.

        Flow:
        1. Check if maintenance mode is active
        2. If not active — pass through immediately
        3. If active — check if user is admin
        4. Admins pass through
        5. Non-admins get maintenance message
        """
        # ── Maintenance mode OFF — pass through immediately ──
        if not settings.MAINTENANCE_MODE:
            return

        # ── No user in update — skip ──
        if not update.effective_user:
            return

        user_id = update.effective_user.id

        # ── Admins always pass through ──
        if settings.is_admin(user_id):
            logger.debug(
                f"🔧 Maintenance mode ON — admin {user_id} passed through"
            )
            return

        # ── Non-admin user — send maintenance message ──
        logger.info(
            f"🔧 Maintenance mode — blocked user {user_id}"
        )

        await self._send_maintenance_message(update, context)

    # ================================================================
    #   MAINTENANCE MESSAGE
    # ================================================================

    async def _send_maintenance_message(
        self,
        update:  Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Send maintenance notification to blocked user.
        Handles both message and callback query updates.
        """
        maintenance_text = (
            f"{EmojiConstants.MAINTENANCE} *Bot Under Maintenance*\n\n"
            f"{settings.MAINTENANCE_MESSAGE}\n\n"
            f"_Please try again later. We apologize for the inconvenience._"
        )

        try:
            # ── Callback query — show alert popup ──
            if update.callback_query:
                await update.callback_query.answer(
                    text=       "🔧 Bot is under maintenance. Please try again later.",
                    show_alert= True,
                )
                return

            # ── Regular message — reply with maintenance text ──
            if update.message:
                await update.message.reply_text(
                    maintenance_text,
                    parse_mode= "Markdown",
                )
                return

        except Exception as e:
            logger.warning(
                f"Could not send maintenance message "
                f"to user {update.effective_user.id}: {e}"
            )