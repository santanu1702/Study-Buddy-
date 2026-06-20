# ============================================================
#         StudyBuddyV3BOT — User Repository
#         All database operations for the users collection
#         Async Motor-based CRUD + ban management
# ============================================================

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from database.connection import db_manager
from database.models import UserModel, utcnow_naive
from config.constants import Collections, UserRole
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   USER REPOSITORY
# ============================================================

class UserRepository:
    """
    Handles all database operations for the users collection.

    Responsibilities:
    - Register new users
    - Fetch user by ID
    - Update user fields
    - Ban / Unban users
    - Track activity & stats
    - Query users for admin panel

    Usage:
        from database.repositories import user_repo
        user = await user_repo.get_by_id(12345)
    """

    def __init__(self) -> None:
        self._collection_name = Collections.USERS

    @property
    def collection(self):
        """Return the users collection from active DB connection."""
        return db_manager.get_collection(self._collection_name)

    # ================================================================
    #   CREATE / REGISTER
    # ================================================================

    async def create(self, user: UserModel) -> UserModel:
        """
        Insert a new user document into the database.
        Silently ignores duplicate key errors (user already exists).

        Args:
            user: UserModel instance to insert

        Returns:
            The inserted UserModel
        """
        try:
            await self.collection.insert_one(user.to_dict())
            logger.info(
                f"✅ New user registered | "
                f"ID: {user.user_id} | "
                f"Name: {user.display_name}"
            )
            return user

        except DuplicateKeyError:
            # User already exists — not an error
            logger.debug(
                f"User {user.user_id} already exists — skipping insert."
            )
            return user

        except PyMongoError as e:
            logger.error(f"DB error creating user {user.user_id}: {e}")
            raise

    async def get_or_create(self, tg_user) -> tuple[UserModel, bool]:
        """
        Get existing user or create new one from Telegram User object.
        This is the primary entry point called on every /start.

        Args:
            tg_user: telegram.User object

        Returns:
            Tuple of (UserModel, is_new_user: bool)
        """
        existing = await self.get_by_id(tg_user.id)

        if existing:
            # Update name/username in case they changed
            await self.update_profile(
                user_id=    tg_user.id,
                first_name= tg_user.first_name or "",
                last_name=  tg_user.last_name,
                username=   tg_user.username,
                full_name=  tg_user.full_name or tg_user.first_name or "",
            )
            return existing, False

        # Create new user
        new_user = UserModel.from_telegram_user(tg_user)
        created  = await self.create(new_user)
        return created, True

    # ================================================================
    #   READ / FETCH
    # ================================================================

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        Fetch a user by their Telegram user ID.

        Args:
            user_id: Telegram numeric user ID

        Returns:
            UserModel if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"user_id": user_id})
            if doc:
                return UserModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(f"DB error fetching user {user_id}: {e}")
            return None

    async def get_by_username(
        self, username: str
    ) -> Optional[UserModel]:
        """
        Fetch a user by their Telegram username (without @).

        Args:
            username: Telegram username string

        Returns:
            UserModel if found, None otherwise
        """
        try:
            # Case-insensitive search
            doc = await self.collection.find_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}}
            )
            if doc:
                return UserModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(f"DB error fetching user by username {username}: {e}")
            return None

    async def get_all(
        self,
        skip:  int = 0,
        limit: int = 100,
    ) -> List[UserModel]:
        """
        Fetch all users with pagination.

        Args:
            skip:  Number of documents to skip
            limit: Max documents to return

        Returns:
            List of UserModel instances
        """
        try:
            cursor = (
                self.collection
                .find({})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [UserModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching all users: {e}")
            return []

    async def get_active_users(
        self,
        hours: int = 24,
    ) -> List[UserModel]:
        """
        Fetch users who were active within the last N hours.

        Args:
            hours: Lookback window in hours (default: 24)

        Returns:
            List of active UserModel instances
        """
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            cursor = self.collection.find(
                {
                    "last_active": {"$gte": cutoff},
                    "is_banned":   False,
                }
            ).sort("last_active", -1)

            docs = await cursor.to_list(length=None)
            return [UserModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching active users: {e}")
            return []

    async def get_broadcast_recipients(self) -> List[UserModel]:
        """
        Fetch all users eligible to receive broadcast messages.
        Excludes banned users and those who disabled notifications.

        Returns:
            List of eligible UserModel instances
        """
        try:
            cursor = self.collection.find(
                {
                    "is_banned":             False,
                    "notifications_enabled": True,
                }
            )
            docs = await cursor.to_list(length=None)
            return [UserModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching broadcast recipients: {e}")
            return []

    async def get_banned_users(
        self,
        skip:  int = 0,
        limit: int = 20,
    ) -> List[UserModel]:
        """
        Fetch all banned users with pagination.

        Args:
            skip:  Pagination offset
            limit: Max results

        Returns:
            List of banned UserModel instances
        """
        try:
            cursor = (
                self.collection
                .find({"is_banned": True})
                .sort("banned_at", -1)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [UserModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching banned users: {e}")
            return []

    # ================================================================
    #   UPDATE
    # ================================================================

    async def update(
        self,
        user_id: int,
        updates: Dict[str, Any],
    ) -> Optional[UserModel]:
        """
        Generic update method — apply any field updates to a user.

        Args:
            user_id: Target user's Telegram ID
            updates: Dict of fields to update

        Returns:
            Updated UserModel or None if not found
        """
        try:
            updates["updated_at"] = utcnow_naive()

            doc = await self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )

            if doc:
                return UserModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(f"DB error updating user {user_id}: {e}")
            return None

    async def update_profile(
        self,
        user_id:    int,
        first_name: str            = "",
        last_name:  Optional[str]  = None,
        username:   Optional[str]  = None,
        full_name:  str            = "",
    ) -> None:
        """
        Update a user's Telegram profile fields.
        Called on every interaction to keep data fresh.
        """
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "first_name": first_name,
                        "last_name":  last_name,
                        "username":   username,
                        "full_name":  full_name,
                        "updated_at": utcnow_naive(),
                    }
                },
            )
        except PyMongoError as e:
            logger.error(f"DB error updating profile for {user_id}: {e}")

    async def update_last_active(self, user_id: int) -> None:
        """
        Update the last_active timestamp for a user.
        Called on every message received.

        Args:
            user_id: Telegram user ID
        """
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "last_active": utcnow_naive(),
                        "updated_at":  utcnow_naive(),
                    },
                    "$inc": {"message_count": 1},
                },
            )
        except PyMongoError as e:
            logger.error(
                f"DB error updating last_active for {user_id}: {e}"
            )

    async def increment_ai_requests(self, user_id: int) -> None:
        """
        Increment the AI request counter for a user.
        Called after every successful AI response.

        Args:
            user_id: Telegram user ID
        """
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"ai_requests": 1},
                    "$set": {"updated_at": utcnow_naive()},
                },
            )
        except PyMongoError as e:
            logger.error(
                f"DB error incrementing AI requests for {user_id}: {e}"
            )

    async def update_language(
        self,
        user_id:  int,
        language: str,
    ) -> bool:
        """
        Update a user's preferred language.

        Args:
            user_id:  Telegram user ID
            language: Language code (en, hi, bn, ar)

        Returns:
            True if updated successfully
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "language_code": language,
                        "updated_at":    utcnow_naive(),
                    }
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error updating language for {user_id}: {e}"
            )
            return False

    async def update_notes_count(
        self,
        user_id: int,
        delta:   int,
    ) -> None:
        """
        Increment or decrement the notes_count for a user.

        Args:
            user_id: Telegram user ID
            delta:   +1 to increment, -1 to decrement
        """
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"notes_count": delta},
                    "$set": {"updated_at": utcnow_naive()},
                },
            )
        except PyMongoError as e:
            logger.error(
                f"DB error updating notes_count for {user_id}: {e}"
            )

    async def toggle_notifications(
        self,
        user_id: int,
        enabled: bool,
    ) -> bool:
        """
        Enable or disable broadcast notifications for a user.

        Args:
            user_id: Telegram user ID
            enabled: True to enable, False to disable

        Returns:
            True if updated successfully
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "notifications_enabled": enabled,
                        "updated_at":            utcnow_naive(),
                    }
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error toggling notifications for {user_id}: {e}"
            )
            return False

    # ================================================================
    #   BAN / UNBAN
    # ================================================================

    async def ban(
        self,
        user_id:    int,
        admin_id:   int,
        reason:     Optional[str] = None,
    ) -> bool:
        """
        Ban a user from using the bot.

        Args:
            user_id:  Target user's Telegram ID
            admin_id: Admin performing the ban
            reason:   Optional ban reason

        Returns:
            True if banned successfully, False if user not found
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_banned":  True,
                        "role":       UserRole.BANNED.value,
                        "ban_reason": reason,
                        "banned_at":  utcnow_naive(),
                        "banned_by":  admin_id,
                        "updated_at": utcnow_naive(),
                    }
                },
            )

            success = result.modified_count > 0
            if success:
                logger.info(
                    f"🔨 User {user_id} banned by admin {admin_id} | "
                    f"Reason: {reason or 'No reason given'}"
                )
            else:
                logger.warning(
                    f"Ban failed — user {user_id} not found in DB."
                )
            return success

        except PyMongoError as e:
            logger.error(f"DB error banning user {user_id}: {e}")
            return False

    async def unban(
        self,
        user_id:  int,
        admin_id: int,
    ) -> bool:
        """
        Unban a previously banned user.

        Args:
            user_id:  Target user's Telegram ID
            admin_id: Admin performing the unban

        Returns:
            True if unbanned successfully
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_banned":  False,
                        "role":       UserRole.USER.value,
                        "ban_reason": None,
                        "banned_at":  None,
                        "banned_by":  None,
                        "updated_at": utcnow_naive(),
                    }
                },
            )

            success = result.modified_count > 0
            if success:
                logger.info(
                    f"🔓 User {user_id} unbanned by admin {admin_id}"
                )
            return success

        except PyMongoError as e:
            logger.error(f"DB error unbanning user {user_id}: {e}")
            return False

    async def is_banned(self, user_id: int) -> bool:
        """
        Quick check if a user is banned.
        Optimized — only fetches the is_banned field.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is banned
        """
        try:
            doc = await self.collection.find_one(
                {"user_id": user_id},
                {"is_banned": 1, "_id": 0},  # Only fetch is_banned field
            )
            if doc:
                return doc.get("is_banned", False)
            return False

        except PyMongoError as e:
            logger.error(f"DB error checking ban for {user_id}: {e}")
            return False

    # ================================================================
    #   STATISTICS
    # ================================================================

    async def count_total(self) -> int:
        """
        Return total number of registered users.

        Returns:
            Integer count of all users
        """
        try:
            return await self.collection.count_documents({})
        except PyMongoError as e:
            logger.error(f"DB error counting total users: {e}")
            return 0

    async def count_active(self, hours: int = 24) -> int:
        """
        Return count of users active in the last N hours.

        Args:
            hours: Lookback window in hours

        Returns:
            Integer count of active users
        """
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return await self.collection.count_documents(
                {
                    "last_active": {"$gte": cutoff},
                    "is_banned":   False,
                }
            )
        except PyMongoError as e:
            logger.error(f"DB error counting active users: {e}")
            return 0

    async def count_banned(self) -> int:
        """
        Return total number of banned users.

        Returns:
            Integer count of banned users
        """
        try:
            return await self.collection.count_documents({"is_banned": True})
        except PyMongoError as e:
            logger.error(f"DB error counting banned users: {e}")
            return 0

    async def get_stats_summary(self) -> Dict[str, Any]:
        """
        Return a complete user statistics summary for the admin panel.

        Returns:
            Dict with total, active_24h, active_7d, banned counts
        """
        try:
            total        = await self.count_total()
            active_24h   = await self.count_active(hours=24)
            active_7d    = await self.count_active(hours=168)
            banned_count = await self.count_banned()

            # New users in last 24h
            cutoff_24h = datetime.utcnow() - timedelta(hours=24)
            new_today = await self.collection.count_documents(
                {"created_at": {"$gte": cutoff_24h}}
            )

            # New users in last 7 days
            cutoff_7d = datetime.utcnow() - timedelta(days=7)
            new_week = await self.collection.count_documents(
                {"created_at": {"$gte": cutoff_7d}}
            )

            return {
                "total":       total,
                "active_24h":  active_24h,
                "active_7d":   active_7d,
                "banned":      banned_count,
                "new_today":   new_today,
                "new_week":    new_week,
            }

        except PyMongoError as e:
            logger.error(f"DB error getting user stats summary: {e}")
            return {
                "total":      0,
                "active_24h": 0,
                "active_7d":  0,
                "banned":     0,
                "new_today":  0,
                "new_week":   0,
            }

    async def get_top_active_users(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Return top N most active users by message count.

        Args:
            limit: Number of top users to return

        Returns:
            List of dicts with user_id, display_name, message_count
        """
        try:
            cursor = (
                self.collection
                .find(
                    {"is_banned": False},
                    {
                        "user_id":       1,
                        "full_name":     1,
                        "username":      1,
                        "message_count": 1,
                        "ai_requests":   1,
                        "_id":           0,
                    },
                )
                .sort("message_count", -1)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return docs

        except PyMongoError as e:
            logger.error(f"DB error fetching top active users: {e}")
            return []

    # ================================================================
    #   DELETE
    # ================================================================

    async def delete(self, user_id: int) -> bool:
        """
        Permanently delete a user from the database.
        Use with caution — prefer ban over delete.

        Args:
            user_id: Telegram user ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            result = await self.collection.delete_one(
                {"user_id": user_id}
            )
            success = result.deleted_count > 0
            if success:
                logger.warning(
                    f"⚠️  User {user_id} permanently deleted from DB."
                )
            return success

        except PyMongoError as e:
            logger.error(f"DB error deleting user {user_id}: {e}")
            return False

    async def exists(self, user_id: int) -> bool:
        """
        Check if a user exists in the database.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user exists
        """
        try:
            count = await self.collection.count_documents(
                {"user_id": user_id},
                limit=1,
            )
            return count > 0

        except PyMongoError as e:
            logger.error(f"DB error checking existence of {user_id}: {e}")
            return False
