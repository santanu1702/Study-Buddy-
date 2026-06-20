# ============================================================
#         StudyBuddyV3BOT — Admin Repository
#         All database operations for admin panel
#         Logs, broadcasts, API stats, system monitoring
# ============================================================

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from database.connection import db_manager
from database.models import (
    AdminLogModel,
    BroadcastModel,
    APIStatsModel,
    utcnow_naive,
)
from config.constants import Collections
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   ADMIN REPOSITORY
# ============================================================

class AdminRepository:
    """
    Handles all database operations for the admin panel.

    Responsibilities:
    - Log all admin actions (audit trail)
    - Record and track broadcasts
    - Track OpenAI API usage stats
    - Fetch error logs
    - System-wide statistics

    Usage:
        from database.repositories import admin_repo
        await admin_repo.log_action(admin_id=123, action="ban_user")
    """

    def __init__(self) -> None:
        self._logs_collection       = Collections.ADMIN_LOGS
        self._broadcasts_collection = Collections.BROADCASTS
        self._api_stats_collection  = Collections.API_STATS

    # ================================================================
    #   COLLECTION ACCESSORS
    # ================================================================

    @property
    def logs_col(self):
        """Return admin_logs collection."""
        return db_manager.get_collection(self._logs_collection)

    @property
    def broadcasts_col(self):
        """Return broadcasts collection."""
        return db_manager.get_collection(self._broadcasts_collection)

    @property
    def api_stats_col(self):
        """Return api_stats collection."""
        return db_manager.get_collection(self._api_stats_collection)

    # ================================================================
    #   ADMIN ACTION LOGS
    # ================================================================

    async def log_action(
        self,
        admin_id:  int,
        action:    str,
        target_id: Optional[int]   = None,
        details:   Optional[Dict]  = None,
        result:    str             = "success",
        error_msg: Optional[str]   = None,
    ) -> Optional[AdminLogModel]:
        """
        Log an admin action to the audit trail.
        Called after every admin panel action.

        Args:
            admin_id:  Admin's Telegram user ID
            action:    Action string (from AdminAction enum)
            target_id: Target user ID if applicable
            details:   Additional action metadata
            result:    "success" or "failure"
            error_msg: Error message if result is "failure"

        Returns:
            Created AdminLogModel or None on failure
        """
        try:
            log = AdminLogModel(
                log_id=    str(uuid.uuid4()),
                admin_id=  admin_id,
                action=    action,
                target_id= target_id,
                details=   details or {},
                result=    result,
                error_msg= error_msg,
            )

            await self.logs_col.insert_one(log.to_dict())

            logger.info(
                f"📋 Admin log | "
                f"Admin: {admin_id} | "
                f"Action: {action} | "
                f"Result: {result}"
            )
            return log

        except PyMongoError as e:
            logger.error(f"DB error logging admin action: {e}")
            return None

    async def get_recent_logs(
        self,
        limit: int = 50,
        skip:  int = 0,
    ) -> List[AdminLogModel]:
        """
        Fetch the most recent admin action logs.

        Args:
            limit: Max logs to return
            skip:  Pagination offset

        Returns:
            List of AdminLogModel instances (newest first)
        """
        try:
            cursor = (
                self.logs_col
                .find({})
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [AdminLogModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching admin logs: {e}")
            return []

    async def get_logs_by_admin(
        self,
        admin_id: int,
        limit:    int = 20,
    ) -> List[AdminLogModel]:
        """
        Fetch logs filtered by a specific admin.

        Args:
            admin_id: Admin's Telegram user ID
            limit:    Max logs to return

        Returns:
            List of AdminLogModel instances
        """
        try:
            cursor = (
                self.logs_col
                .find({"admin_id": admin_id})
                .sort("created_at", DESCENDING)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [AdminLogModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error fetching logs for admin {admin_id}: {e}"
            )
            return []

    async def get_logs_by_action(
        self,
        action: str,
        limit:  int = 20,
    ) -> List[AdminLogModel]:
        """
        Fetch logs filtered by action type.

        Args:
            action: Action string to filter by
            limit:  Max logs to return

        Returns:
            List of AdminLogModel instances
        """
        try:
            cursor = (
                self.logs_col
                .find({"action": action})
                .sort("created_at", DESCENDING)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [AdminLogModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error fetching logs for action {action}: {e}"
            )
            return []

    async def get_failed_logs(
        self,
        limit: int = 20,
    ) -> List[AdminLogModel]:
        """
        Fetch only failed admin action logs.
        Useful for debugging and monitoring.

        Args:
            limit: Max logs to return

        Returns:
            List of failed AdminLogModel instances
        """
        try:
            cursor = (
                self.logs_col
                .find({"result": "failure"})
                .sort("created_at", DESCENDING)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [AdminLogModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching failed logs: {e}")
            return []

    async def count_logs(self) -> int:
        """Return total number of admin log entries."""
        try:
            return await self.logs_col.count_documents({})
        except PyMongoError as e:
            logger.error(f"DB error counting logs: {e}")
            return 0

    async def clear_old_logs(self, days: int = 30) -> int:
        """
        Delete admin logs older than N days.
        Keeps the logs collection from growing too large.

        Args:
            days: Delete logs older than this many days

        Returns:
            Number of logs deleted
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            result = await self.logs_col.delete_many(
                {"created_at": {"$lt": cutoff}}
            )
            count = result.deleted_count
            if count > 0:
                logger.info(
                    f"🧹 Cleared {count} old admin logs "
                    f"(older than {days} days)"
                )
            return count

        except PyMongoError as e:
            logger.error(f"DB error clearing old logs: {e}")
            return 0

    # ================================================================
    #   BROADCAST MANAGEMENT
    # ================================================================

    async def create_broadcast(
        self,
        admin_id:     int,
        message_text: str,
        total_users:  int,
        has_media:    bool         = False,
        media_type:   Optional[str] = None,
    ) -> Optional[BroadcastModel]:
        """
        Create a new broadcast record before sending.
        Tracks the broadcast for admin reporting.

        Args:
            admin_id:     Sending admin's Telegram ID
            message_text: Broadcast message content
            total_users:  Total users targeted
            has_media:    Whether message includes media
            media_type:   Type of media (photo/video/document)

        Returns:
            Created BroadcastModel or None on failure
        """
        try:
            broadcast = BroadcastModel(
                broadcast_id= str(uuid.uuid4()),
                admin_id=     admin_id,
                message_text= message_text,
                total_users=  total_users,
                has_media=    has_media,
                media_type=   media_type,
                status=       "sending",
            )

            await self.broadcasts_col.insert_one(broadcast.to_dict())

            logger.info(
                f"📢 Broadcast created | "
                f"ID: {broadcast.broadcast_id[:8]} | "
                f"Admin: {admin_id} | "
                f"Targets: {total_users}"
            )
            return broadcast

        except PyMongoError as e:
            logger.error(f"DB error creating broadcast: {e}")
            return None

    async def update_broadcast_stats(
        self,
        broadcast_id: str,
        sent_count:   int,
        failed_count: int,
        status:       str = "done",
    ) -> bool:
        """
        Update delivery statistics for a broadcast after completion.

        Args:
            broadcast_id: UUID of the broadcast record
            sent_count:   Number of successful deliveries
            failed_count: Number of failed deliveries
            status:       Final status (done/failed)

        Returns:
            True if updated successfully
        """
        try:
            result = await self.broadcasts_col.update_one(
                {"broadcast_id": broadcast_id},
                {
                    "$set": {
                        "sent_count":   sent_count,
                        "failed_count": failed_count,
                        "status":       status,
                        "completed_at": utcnow_naive(),
                    }
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error updating broadcast {broadcast_id}: {e}"
            )
            return False

    async def get_broadcast_history(
        self,
        limit: int = 10,
        skip:  int = 0,
    ) -> List[BroadcastModel]:
        """
        Fetch broadcast history for the admin panel.

        Args:
            limit: Max records to return
            skip:  Pagination offset

        Returns:
            List of BroadcastModel instances (newest first)
        """
        try:
            cursor = (
                self.broadcasts_col
                .find({})
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [BroadcastModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(f"DB error fetching broadcast history: {e}")
            return []

    async def get_broadcast_by_id(
        self,
        broadcast_id: str,
    ) -> Optional[BroadcastModel]:
        """
        Fetch a single broadcast record by ID.

        Args:
            broadcast_id: UUID of the broadcast

        Returns:
            BroadcastModel or None
        """
        try:
            doc = await self.broadcasts_col.find_one(
                {"broadcast_id": broadcast_id}
            )
            if doc:
                return BroadcastModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(
                f"DB error fetching broadcast {broadcast_id}: {e}"
            )
            return None

    async def get_broadcast_stats_summary(self) -> Dict[str, Any]:
        """
        Return broadcast statistics summary for admin panel.

        Returns:
            Dict with total_broadcasts, total_sent, total_failed,
            last_broadcast_at
        """
        try:
            total_broadcasts = await self.broadcasts_col.count_documents({})

            # Aggregate totals
            pipeline = [
                {
                    "$group": {
                        "_id":          None,
                        "total_sent":   {"$sum": "$sent_count"},
                        "total_failed": {"$sum": "$failed_count"},
                    }
                }
            ]
            agg_result = await self.broadcasts_col.aggregate(
                pipeline
            ).to_list(length=1)

            totals = agg_result[0] if agg_result else {}

            # Last broadcast
            last_doc = await self.broadcasts_col.find_one(
                {},
                sort=[("created_at", DESCENDING)]
            )
            last_at = last_doc.get("created_at") if last_doc else None

            return {
                "total_broadcasts": total_broadcasts,
                "total_sent":       totals.get("total_sent", 0),
                "total_failed":     totals.get("total_failed", 0),
                "last_broadcast_at": last_at,
            }

        except PyMongoError as e:
            logger.error(f"DB error getting broadcast stats: {e}")
            return {
                "total_broadcasts":  0,
                "total_sent":        0,
                "total_failed":      0,
                "last_broadcast_at": None,
            }

    # ================================================================
    #   API USAGE STATS
    # ================================================================

    async def record_api_usage(
        self,
        user_id:           int,
        prompt_tokens:     int,
        completion_tokens: int,
        model:             str = "gpt-4o-mini",
    ) -> bool:
        """
        Record OpenAI API usage for a user on today's date.
        Uses upsert to accumulate daily totals.

        Args:
            user_id:           Telegram user ID
            prompt_tokens:     Tokens used in the prompt
            completion_tokens: Tokens in the completion
            model:             OpenAI model used

        Returns:
            True if recorded successfully
        """
        try:
            today       = datetime.utcnow().strftime("%Y-%m-%d")
            total_tokens = prompt_tokens + completion_tokens

            # Approximate cost calculation for gpt-4o-mini
            # Input: $0.15/1M tokens, Output: $0.60/1M tokens
            estimated_cost = (
                (prompt_tokens     / 1_000_000) * 0.15 +
                (completion_tokens / 1_000_000) * 0.60
            )

            result = await self.api_stats_col.update_one(
                {
                    "user_id": user_id,
                    "date":    today,
                },
                {
                    "$inc": {
                        "requests_count":      1,
                        "tokens_used":         total_tokens,
                        "prompt_tokens":       prompt_tokens,
                        "completion_tokens":   completion_tokens,
                        "estimated_cost_usd":  estimated_cost,
                    },
                    "$set": {
                        "updated_at": utcnow_naive(),
                    },
                    "$setOnInsert": {
                        "created_at": utcnow_naive(),
                    },
                },
                upsert=True,    # Create doc if it doesn't exist
            )

            return result.acknowledged

        except PyMongoError as e:
            logger.error(
                f"DB error recording API usage for {user_id}: {e}"
            )
            return False

    async def get_api_stats_today(self) -> Dict[str, Any]:
        """
        Get aggregated API usage stats for today.

        Returns:
            Dict with total_requests, total_tokens,
            total_cost_usd, unique_users
        """
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")

            pipeline = [
                {"$match": {"date": today}},
                {
                    "$group": {
                        "_id":              None,
                        "total_requests":   {"$sum": "$requests_count"},
                        "total_tokens":     {"$sum": "$tokens_used"},
                        "total_cost_usd":   {"$sum": "$estimated_cost_usd"},
                        "unique_users":     {"$sum": 1},
                    }
                },
            ]

            result = await self.api_stats_col.aggregate(
                pipeline
            ).to_list(length=1)

            if result:
                data = result[0]
                return {
                    "date":           today,
                    "total_requests": data.get("total_requests", 0),
                    "total_tokens":   data.get("total_tokens", 0),
                    "total_cost_usd": round(
                        data.get("total_cost_usd", 0.0), 6
                    ),
                    "unique_users":   data.get("unique_users", 0),
                }

            return {
                "date":           today,
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
                "unique_users":   0,
            }

        except PyMongoError as e:
            logger.error(f"DB error getting today's API stats: {e}")
            return {
                "date":           datetime.utcnow().strftime("%Y-%m-%d"),
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
                "unique_users":   0,
            }

    async def get_api_stats_range(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Get daily API usage stats for the last N days.
        Used to show usage trends in admin panel.

        Args:
            days: Number of days to look back

        Returns:
            List of daily stats dicts, newest first
        """
        try:
            # Generate date strings for the range
            date_range = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(days)
            ]

            pipeline = [
                {"$match": {"date": {"$in": date_range}}},
                {
                    "$group": {
                        "_id":            "$date",
                        "total_requests": {"$sum": "$requests_count"},
                        "total_tokens":   {"$sum": "$tokens_used"},
                        "total_cost_usd": {"$sum": "$estimated_cost_usd"},
                        "unique_users":   {"$sum": 1},
                    }
                },
                {"$sort": {"_id": DESCENDING}},
            ]

            results = await self.api_stats_col.aggregate(
                pipeline
            ).to_list(length=days)

            return [
                {
                    "date":           r["_id"],
                    "total_requests": r.get("total_requests", 0),
                    "total_tokens":   r.get("total_tokens", 0),
                    "total_cost_usd": round(
                        r.get("total_cost_usd", 0.0), 6
                    ),
                    "unique_users":   r.get("unique_users", 0),
                }
                for r in results
            ]

        except PyMongoError as e:
            logger.error(f"DB error getting API stats range: {e}")
            return []

    async def get_api_stats_total(self) -> Dict[str, Any]:
        """
        Get all-time aggregated API usage statistics.

        Returns:
            Dict with lifetime totals for requests,
            tokens, cost, and unique users
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id":              None,
                        "total_requests":   {"$sum": "$requests_count"},
                        "total_tokens":     {"$sum": "$tokens_used"},
                        "total_cost_usd":   {"$sum": "$estimated_cost_usd"},
                        "unique_users":     {
                            "$addToSet": "$user_id"
                        },
                    }
                },
            ]

            result = await self.api_stats_col.aggregate(
                pipeline
            ).to_list(length=1)

            if result:
                data = result[0]
                unique_users = data.get("unique_users", [])
                return {
                    "total_requests":   data.get("total_requests", 0),
                    "total_tokens":     data.get("total_tokens", 0),
                    "total_cost_usd":   round(
                        data.get("total_cost_usd", 0.0), 4
                    ),
                    "unique_users":     len(unique_users),
                }

            return {
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
                "unique_users":   0,
            }

        except PyMongoError as e:
            logger.error(f"DB error getting total API stats: {e}")
            return {
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
                "unique_users":   0,
            }

    async def get_top_api_users(
        self,
        limit: int = 10,
        days:  int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Get top users by API usage in the last N days.
        Used in admin panel to identify heavy users.

        Args:
            limit: Number of top users to return
            days:  Lookback window in days

        Returns:
            List of dicts with user_id and usage stats
        """
        try:
            date_range = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(days)
            ]

            pipeline = [
                {"$match": {"date": {"$in": date_range}}},
                {
                    "$group": {
                        "_id":            "$user_id",
                        "total_requests": {"$sum": "$requests_count"},
                        "total_tokens":   {"$sum": "$tokens_used"},
                        "total_cost_usd": {"$sum": "$estimated_cost_usd"},
                    }
                },
                {"$sort": {"total_requests": DESCENDING}},
                {"$limit": limit},
            ]

            results = await self.api_stats_col.aggregate(
                pipeline
            ).to_list(length=limit)

            return [
                {
                    "user_id":        r["_id"],
                    "total_requests": r.get("total_requests", 0),
                    "total_tokens":   r.get("total_tokens", 0),
                    "total_cost_usd": round(
                        r.get("total_cost_usd", 0.0), 6
                    ),
                }
                for r in results
            ]

        except PyMongoError as e:
            logger.error(f"DB error getting top API users: {e}")
            return []

    async def get_user_api_stats(
        self,
        user_id: int,
        days:    int = 30,
    ) -> Dict[str, Any]:
        """
        Get API usage stats for a specific user.

        Args:
            user_id: Telegram user ID
            days:    Lookback window in days

        Returns:
            Dict with user's total API usage
        """
        try:
            date_range = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(days)
            ]

            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "date":    {"$in": date_range},
                    }
                },
                {
                    "$group": {
                        "_id":            None,
                        "total_requests": {"$sum": "$requests_count"},
                        "total_tokens":   {"$sum": "$tokens_used"},
                        "total_cost_usd": {"$sum": "$estimated_cost_usd"},
                    }
                },
            ]

            result = await self.api_stats_col.aggregate(
                pipeline
            ).to_list(length=1)

            if result:
                data = result[0]
                return {
                    "user_id":        user_id,
                    "period_days":    days,
                    "total_requests": data.get("total_requests", 0),
                    "total_tokens":   data.get("total_tokens", 0),
                    "total_cost_usd": round(
                        data.get("total_cost_usd", 0.0), 6
                    ),
                }

            return {
                "user_id":        user_id,
                "period_days":    days,
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
            }

        except PyMongoError as e:
            logger.error(
                f"DB error getting API stats for user {user_id}: {e}"
            )
            return {
                "user_id":        user_id,
                "period_days":    days,
                "total_requests": 0,
                "total_tokens":   0,
                "total_cost_usd": 0.0,
            }

    # ================================================================
    #   SYSTEM-WIDE STATS
    # ================================================================

    async def get_full_system_stats(self) -> Dict[str, Any]:
        """
        Compile a complete system statistics report.
        Used for the main admin panel dashboard.

        Returns:
            Dict with all system metrics combined
        """
        try:
            # Database stats
            db_stats = await db_manager.get_stats()

            # API stats
            api_today = await self.get_api_stats_today()
            api_total = await self.get_api_stats_total()

            # Broadcast stats
            broadcast_stats = await self.get_broadcast_stats_summary()

            # Log stats
            total_logs = await self.count_logs()

            return {
                "database":   db_stats,
                "api_today":  api_today,
                "api_total":  api_total,
                "broadcasts": broadcast_stats,
                "logs":       {"total": total_logs},
                "generated_at": utcnow_naive().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error compiling system stats: {e}")
            return {"error": str(e)}

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get a lightweight summary for the admin dashboard.
        Faster than get_full_system_stats — fewer queries.

        Returns:
            Dict with key metrics for quick display
        """
        try:
            today        = datetime.utcnow().strftime("%Y-%m-%d")
            api_today    = await self.get_api_stats_today()
            total_logs   = await self.count_logs()
            last_broadcast = await self.broadcasts_col.find_one(
                {},
                sort=[("created_at", DESCENDING)]
            )

            return {
                "api_requests_today": api_today.get("total_requests", 0),
                "api_tokens_today":   api_today.get("total_tokens", 0),
                "api_cost_today":     api_today.get("total_cost_usd", 0.0),
                "total_logs":         total_logs,
                "last_broadcast_at":  (
                    last_broadcast.get("created_at")
                    if last_broadcast else None
                ),
                "generated_at":       today,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {
                "api_requests_today": 0,
                "api_tokens_today":   0,
                "api_cost_today":     0.0,
                "total_logs":         0,
                "last_broadcast_at":  None,
                "generated_at":       datetime.utcnow().strftime("%Y-%m-%d"),
            }
