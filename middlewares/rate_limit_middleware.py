# ============================================================
#         StudyBuddyV3BOT — Rate Limit Middleware
#         Anti-spam per-user message rate limiting
#         Runs third — priority group -1
# ============================================================

import time
from collections import defaultdict
from typing import Dict, Tuple

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings
from config.constants import EmojiConstants, TimeConstants
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   IN-MEMORY RATE LIMIT STORE
#   Fast in-memory tracking — no DB overhead per message
#   Format: {user_id: (message_count, window_start_time)}
# ============================================================

_rate_limit_store: Dict[int, Tuple[int, float]] = defaultdict(
    lambda: (0, time.monotonic())
)


# ============================================================
#   RATE LIMIT MIDDLEWARE
# ============================================================

class RateLimitMiddleware:
    """
    Per-user message rate limiting middleware.

    Tracks message frequency per user using a sliding
    time window stored in memory (no DB overhead).

    When limit exceeded:
    - First violation: sends warning message
    - Subsequent violations: silently ignored
    - Auto-resets after window expires

    Priority group: -1 (runs third, after auth middleware)

    Config (from .env):
        RATE_LIMIT_MESSAGES: Max messages per window (default: 10)
        RATE_LIMIT_COOLDOWN: Window size in seconds (default: 60)
    """

    def __init__(self) -> None:
        self.max_messages = settings.RATE_LIMIT_MESSAGES
        self.window_secs  = settings.RATE_LIMIT_COOLDOWN
        # Track who already got a warning this window
        self._warned: Dict[int, float] = {}

    async def process(
        self,
        update:  Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Main middleware processor.
        Checks and updates rate limit for every update.

        Flow:
        1. Skip non-user updates
        2. Skip admins
        3. Check current window count
        4. If window expired — reset counter
        5. If under limit — increment and pass
        6. If over limit — send warning (first time) or ignore
        """
        # ── Skip non-user updates ──
        if not update.effective_user:
            return

        user_id = update.effective_user.id

        # ── Skip admins ──
        if settings.is_admin(user_id):
            return

        # ── Skip non-message updates (callback queries handled separately) ──
        if not update.message:
            return

        # ── Get current window data ──
        count, window_start = _rate_limit_store[user_id]
        now                 = time.monotonic()
        elapsed             = now - window_start

        # ── Window expired — reset ──
        if elapsed >= self.window_secs:
            _rate_limit_store[user_id] = (1, now)
            # Clear warned status for new window
            self._warned.pop(user_id, None)
            return

        # ── Under limit — increment and pass ──
        if count < self.max_messages:
            _rate_limit_store[user_id] = (count + 1, window_start)
            return

        # ── Over limit — handle violation ──
        await self._handle_rate_limited(
            update=       update,
            context=      context,
            user_id=      user_id,
            window_start= window_start,
            now=          now,
        )

    # ================================================================
    #   RATE LIMIT HANDLER
    # ================================================================

    async def _handle_rate_limited(
        self,
        update:       Update,
        context:      ContextTypes.DEFAULT_TYPE,
        user_id:      int,
        window_start: float,
        now:          float,
    ) -> None:
        """
        Handle a rate-limited user.
        Sends warning only once per window to avoid spam.

        Args:
            update:       Current update
            context:      Handler context
            user_id:      Telegram user ID
            window_start: When current window started
            now:          Current monotonic time
        """
        # Calculate remaining cooldown
        elapsed          = now - window_start
        remaining_secs   = max(0, int(self.window_secs - elapsed))

        # ── Check if already warned this window ──
        last_warned = self._warned.get(user_id, 0)
        already_warned = (now - last_warned) < self.window_secs

        if already_warned:
            # Silently ignore subsequent violations
            logger.debug(
                f"Rate limit — silently ignoring | "
                f"User: {user_id}"
            )
            return

        # ── First violation — send warning ──
        self._warned[user_id] = now

        logger.info(
            f"⚠️ Rate limit exceeded | "
            f"User: {user_id} | "
            f"Limit: {self.max_messages} msgs/{self.window_secs}s | "
            f"Cooldown: {remaining_secs}s"
        )

        warning_text = (
            f"{EmojiConstants.WARNING} *Slow Down!*\n\n"
            f"You are sending messages too fast.\n\n"
            f"⏳ Please wait `{remaining_secs}` seconds "
            f"before sending more messages.\n\n"
            f"_Limit: {self.max_messages} messages "
            f"per {self.window_secs} seconds_"
        )

        try:
            await update.message.reply_text(
                warning_text,
                parse_mode= "Markdown",
            )
        except Exception as e:
            logger.warning(
                f"Could not send rate limit warning "
                f"to user {user_id}: {e}"
            )

    # ================================================================
    #   UTILITY METHODS
    # ================================================================

    def get_user_status(self, user_id: int) -> Dict:
        """
        Get current rate limit status for a user.
        Used for debugging and admin monitoring.

        Args:
            user_id: Telegram user ID

        Returns:
            Dict with count, window_start, remaining, is_limited
        """
        count, window_start = _rate_limit_store[user_id]
        now                 = time.monotonic()
        elapsed             = now - window_start

        if elapsed >= self.window_secs:
            return {
                "count":        0,
                "limit":        self.max_messages,
                "remaining":    self.max_messages,
                "is_limited":   False,
                "resets_in":    0,
            }

        return {
            "count":      count,
            "limit":      self.max_messages,
            "remaining":  max(0, self.max_messages - count),
            "is_limited": count >= self.max_messages,
            "resets_in":  max(0, int(self.window_secs - elapsed)),
        }

    def reset_user(self, user_id: int) -> None:
        """
        Manually reset rate limit for a user.
        Can be called by admin commands.

        Args:
            user_id: Telegram user ID to reset
        """
        _rate_limit_store[user_id] = (0, time.monotonic())
        self._warned.pop(user_id, None)
        logger.info(f"🔄 Rate limit reset for user {user_id}")

    def reset_all(self) -> None:
        """
        Reset rate limits for all users.
        Used during bot restart or admin command.
        """
        _rate_limit_store.clear()
        self._warned.clear()
        logger.info("🔄 All rate limits reset")

    @staticmethod
    def get_store_size() -> int:
        """
        Return number of users currently tracked.
        Used for memory monitoring.
        """
        return len(_rate_limit_store)