# ============================================================
#         StudyBuddyV3BOT — Auth Middleware
#         Runs on every update before handlers
#         Registers users, checks bans, loads language
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from config.constants import EmojiConstants
from database.repositories import user_repo
from handlers.language import LanguageHandler
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   AUTH MIDDLEWARE
# ============================================================

class AuthMiddleware:
    """
    Authentication and registration middleware.

    Runs on every incoming update before any handler.
    Responsibilities:
    1. Register new users automatically
    2. Check if user is banned — block if so
    3. Load user's language preference into session
    4. Update last_active timestamp
    5. Skip processing for non-user updates (channels etc.)

    Priority group: -2 (runs second after maintenance check)
    """

    async def process(
        self,
        update:  Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Main middleware processor.
        Called on every update via MessageHandler(filters.ALL).

        Flow:
        1. Extract user from update
        2. Skip if no user (channel posts etc.)
        3. Skip if admin (always allow)
        4. Register user if new
        5. Check ban status
        6. Load language preference
        7. Update last active
        """
        # ── Skip non-user updates ──
        if not update.effective_user:
            return

        tg_user = update.effective_user
        user_id = tg_user.id

        # ── Skip bots ──
        if tg_user.is_bot:
            return

        # ── Admins always pass through ──
        if settings.is_admin(user_id):
            # Still load language for admins
            await LanguageHandler.load_user_language(update, context)
            return

        try:
            # ── Register or fetch user ──
            user, is_new = await user_repo.get_or_create(tg_user)

            if is_new:
                logger.info(
                    f"👤 New user auto-registered via middleware | "
                    f"ID: {user_id} | "
                    f"Name: {user.display_name}"
                )
                # Auto-detect language for new users
                await LanguageHandler.auto_detect_and_set(
                    update, context
                )
            else:
                # Load saved language preference
                await LanguageHandler.load_user_language(
                    update, context
                )

            # ── Check ban status ──
            if user.is_banned:
                await self._handle_banned_user(update, context, user)
                return

            # ── Update last active (non-blocking) ──
            await user_repo.update_last_active(user_id)

        except Exception as e:
            # Never let middleware crash the bot
            logger.error(
                f"Auth middleware error for user {user_id}: {e}",
                exc_info=True,
            )

    # ================================================================
    #   BAN HANDLER
    # ================================================================

    async def _handle_banned_user(
        self,
        update:  Update,
        context: ContextTypes.DEFAULT_TYPE,
        user,
    ) -> None:
        """
        Handle a banned user trying to use the bot.
        Sends ban notification and stops processing.
        """
        user_id = user.user_id
        lang    = context.user_data.get(
            "language", settings.DEFAULT_LANGUAGE
        )

        logger.warning(
            f"🚫 Banned user attempted access | "
            f"ID: {user_id} | "
            f"Name: {user.display_name}"
        )

        ban_message = (
            f"{EmojiConstants.BAN} *You Have Been Banned*\n\n"
            f"You are not allowed to use this bot.\n\n"
            f"_If you think this is a mistake, "
            f"please contact the administrator._"
        )

        # Send ban message based on context type
        try:
            if update.message:
                await update.message.reply_text(
                    ban_message,
                    parse_mode="Markdown",
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "🚫 You are banned from using this bot.",
                    show_alert=True,
                )
        except Exception as e:
            logger.warning(
                f"Could not send ban message to {user_id}: {e}"
            )