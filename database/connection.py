# ============================================================
#         StudyBuddyV3BOT — MongoDB Async Connection
#         Motor-based async database connection manager
#         with connection pooling, health checks & indexes
# ============================================================

import asyncio
from typing import Optional
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo import IndexModel, ASCENDING, DESCENDING
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    ConfigurationError,
)

from config.settings import settings
from config.constants import Collections
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   DATABASE INDEXES
#   Defined centrally — created on startup automatically
# ============================================================

# Each entry: (collection_name, list of IndexModel)
COLLECTION_INDEXES = {

    # ── Users Collection ──
    Collections.USERS: [
        IndexModel(
            [("user_id", ASCENDING)],
            unique=True,
            name="user_id_unique",
        ),
        IndexModel(
            [("username", ASCENDING)],
            name="username_idx",
            sparse=True,                     # Allow null usernames
        ),
        IndexModel(
            [("role", ASCENDING)],
            name="role_idx",
        ),
        IndexModel(
            [("last_active", DESCENDING)],
            name="last_active_idx",
        ),
        IndexModel(
            [("created_at", DESCENDING)],
            name="created_at_idx",
        ),
        IndexModel(
            [("is_banned", ASCENDING)],
            name="is_banned_idx",
        ),
    ],

    # ── Notes Collection ──
    Collections.NOTES: [
        IndexModel(
            [("user_id", ASCENDING), ("status", ASCENDING)],
            name="user_notes_idx",
        ),
        IndexModel(
            [("user_id", ASCENDING), ("created_at", DESCENDING)],
            name="user_notes_date_idx",
        ),
        IndexModel(
            [("note_id", ASCENDING)],
            unique=True,
            name="note_id_unique",
        ),
        IndexModel(
            [("created_at", DESCENDING)],
            name="notes_created_at_idx",
        ),
    ],

    # ── AI Context Collection ──
    Collections.AI_CONTEXT: [
        IndexModel(
            [("user_id", ASCENDING)],
            unique=True,
            name="ai_context_user_unique",
        ),
        IndexModel(
            [("updated_at", ASCENDING)],
            expireAfterSeconds=settings.AI_CONTEXT_EXPIRY,  # TTL index — auto cleanup
            name="ai_context_ttl",
        ),
    ],

    # ── Admin Logs Collection ──
    Collections.ADMIN_LOGS: [
        IndexModel(
            [("created_at", DESCENDING)],
            name="admin_logs_date_idx",
        ),
        IndexModel(
            [("admin_id", ASCENDING)],
            name="admin_logs_admin_idx",
        ),
        IndexModel(
            [("action", ASCENDING)],
            name="admin_logs_action_idx",
        ),
    ],

    # ── Broadcasts Collection ──
    Collections.BROADCASTS: [
        IndexModel(
            [("created_at", DESCENDING)],
            name="broadcasts_date_idx",
        ),
        IndexModel(
            [("admin_id", ASCENDING)],
            name="broadcasts_admin_idx",
        ),
        IndexModel(
            [("status", ASCENDING)],
            name="broadcasts_status_idx",
        ),
    ],

    # ── API Stats Collection ──
    Collections.API_STATS: [
        IndexModel(
            [("user_id", ASCENDING), ("date", DESCENDING)],
            name="api_stats_user_date_idx",
        ),
        IndexModel(
            [("date", DESCENDING)],
            name="api_stats_date_idx",
        ),
    ],

    # ── Rate Limits Collection ──
    Collections.RATE_LIMITS: [
        IndexModel(
            [("user_id", ASCENDING), ("window", ASCENDING)],
            unique=True,
            name="rate_limits_user_window_unique",
        ),
        IndexModel(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,            # TTL — expire at field value
            name="rate_limits_ttl",
        ),
    ],
}


# ============================================================
#   DATABASE MANAGER CLASS
# ============================================================

class DatabaseManager:
    """
    Async MongoDB connection manager for StudyBuddyV3BOT.

    Responsibilities:
    - Manage Motor client lifecycle (connect / disconnect)
    - Provide database and collection accessors
    - Create all indexes on startup
    - Health check support
    - Connection pooling configuration

    Usage:
        await db_manager.connect()
        db = db_manager.database
        collection = db_manager.get_collection("users")
        await db_manager.disconnect()
    """

    def __init__(self) -> None:
        self._client:   Optional[AsyncIOMotorClient]   = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._is_connected: bool = False

    # ================================================================
    #   CONNECTION LIFECYCLE
    # ================================================================

    async def connect(self) -> None:
        """
        Establish async connection to MongoDB Atlas.
        Creates indexes after successful connection.
        Raises ConnectionFailure if connection cannot be established.
        """
        if self._is_connected:
            logger.warning("Database already connected — skipping reconnect.")
            return

        logger.info("🔌 Connecting to MongoDB...")

        try:
            # ── Create Motor client with connection pool settings ──
            self._client = AsyncIOMotorClient(
                settings.mongo_uri,

                # Connection pool
                maxPoolSize=50,              # Max concurrent connections
                minPoolSize=5,               # Keep minimum connections alive
                maxIdleTimeMS=45000,         # Close idle connections after 45s

                # Timeouts
                serverSelectionTimeoutMS=10000,   # 10s to find server
                connectTimeoutMS=10000,            # 10s to establish connection
                socketTimeoutMS=30000,             # 30s for operations

                # Reliability
                retryWrites=True,            # Retry failed writes
                retryReads=True,             # Retry failed reads

                # App identification (visible in Atlas monitoring)
                appName="StudyBuddyV3BOT",
            )

            # ── Select the database ──
            self._database = self._client[settings.DB_NAME]

            # ── Verify connection with a ping ──
            await self._client.admin.command("ping")

            self._is_connected = True
            logger.info(
                f"✅ MongoDB connected | "
                f"DB: {settings.DB_NAME} | "
                f"Host: {self._get_masked_host()}"
            )

            # ── Create all collection indexes ──
            await self._create_indexes()

        except ServerSelectionTimeoutError as e:
            logger.critical(
                f"❌ MongoDB server not reachable: {e}\n"
                f"   Check MONGO_URI and network access in Atlas."
            )
            raise ConnectionFailure(
                f"Cannot reach MongoDB server: {e}"
            ) from e

        except ConfigurationError as e:
            logger.critical(f"❌ MongoDB configuration error: {e}")
            raise

        except Exception as e:
            logger.critical(f"❌ Unexpected MongoDB connection error: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Gracefully close the MongoDB connection.
        Called during bot shutdown in main.py.
        """
        if not self._is_connected or self._client is None:
            logger.warning("Database not connected — nothing to disconnect.")
            return

        try:
            self._client.close()
            self._is_connected = False
            self._client   = None
            self._database = None
            logger.info("✅ MongoDB disconnected cleanly.")

        except Exception as e:
            logger.error(f"Error during MongoDB disconnect: {e}")

    async def reconnect(self) -> None:
        """
        Disconnect and reconnect.
        Useful for recovering from connection drops.
        """
        logger.info("🔄 Reconnecting to MongoDB...")
        await self.disconnect()
        await asyncio.sleep(2)               # Brief pause before reconnect
        await self.connect()

    # ================================================================
    #   ACCESSORS
    # ================================================================

    @property
    def client(self) -> AsyncIOMotorClient:
        """Return the raw Motor client."""
        self._assert_connected()
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Return the active Motor database instance."""
        self._assert_connected()
        return self._database

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        """
        Return a Motor collection by name.

        Usage:
            col = db_manager.get_collection(Collections.USERS)
            await col.find_one({"user_id": 12345})
        """
        self._assert_connected()
        return self._database[name]

    @property
    def is_connected(self) -> bool:
        """True if database is currently connected."""
        return self._is_connected

    # ================================================================
    #   INDEX CREATION
    # ================================================================

    async def _create_indexes(self) -> None:
        """
        Create all defined indexes for all collections.
        Uses create_indexes() which is idempotent —
        safe to call on every startup.
        """
        logger.info("📑 Creating database indexes...")
        created_count = 0
        error_count   = 0

        for collection_name, indexes in COLLECTION_INDEXES.items():
            try:
                collection = self.get_collection(collection_name)
                await collection.create_indexes(indexes)
                created_count += len(indexes)
                logger.debug(
                    f"   ✅ Indexes created for '{collection_name}' "
                    f"({len(indexes)} indexes)"
                )
            except Exception as e:
                error_count += 1
                logger.error(
                    f"   ❌ Failed to create indexes for "
                    f"'{collection_name}': {e}"
                )

        if error_count == 0:
            logger.info(
                f"✅ All indexes ready | "
                f"Collections: {len(COLLECTION_INDEXES)} | "
                f"Total indexes: {created_count}"
            )
        else:
            logger.warning(
                f"⚠️  Index creation completed with {error_count} error(s). "
                f"Check logs for details."
            )

    # ================================================================
    #   HEALTH CHECK
    # ================================================================

    async def health_check(self) -> dict:
        """
        Perform a database health check.
        Returns a dict with status and metadata.

        Usage:
            health = await db_manager.health_check()
            # {"status": "ok", "latency_ms": 12, "db": "studybuddy_db"}
        """
        if not self._is_connected:
            return {
                "status":  "disconnected",
                "latency_ms": None,
                "db":      settings.DB_NAME,
                "error":   "Not connected",
            }

        try:
            import time
            start = time.monotonic()
            await self._client.admin.command("ping")
            latency_ms = round((time.monotonic() - start) * 1000, 2)

            # Get basic server info
            server_info = await self._client.server_info()

            return {
                "status":       "ok",
                "latency_ms":   latency_ms,
                "db":           settings.DB_NAME,
                "mongo_version": server_info.get("version", "unknown"),
                "connected":    True,
            }

        except Exception as e:
            return {
                "status":     "error",
                "latency_ms": None,
                "db":         settings.DB_NAME,
                "error":      str(e),
                "connected":  False,
            }

    # ================================================================
    #   DATABASE STATS
    # ================================================================

    async def get_stats(self) -> dict:
        """
        Retrieve database statistics.
        Used by admin panel for monitoring.
        """
        self._assert_connected()
        try:
            stats = await self._database.command("dbStats")
            collections = await self._database.list_collection_names()

            # Per-collection document counts
            collection_counts = {}
            for col_name in collections:
                try:
                    count = await self._database[col_name].count_documents({})
                    collection_counts[col_name] = count
                except Exception:
                    collection_counts[col_name] = -1

            return {
                "database":          settings.DB_NAME,
                "collections":       len(collections),
                "collection_names":  collections,
                "collection_counts": collection_counts,
                "data_size_mb":      round(
                    stats.get("dataSize", 0) / (1024 * 1024), 2
                ),
                "storage_size_mb":   round(
                    stats.get("storageSize", 0) / (1024 * 1024), 2
                ),
                "indexes":           stats.get("indexes", 0),
                "index_size_mb":     round(
                    stats.get("indexSize", 0) / (1024 * 1024), 2
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}

    # ================================================================
    #   UTILITY METHODS
    # ================================================================

    def _assert_connected(self) -> None:
        """
        Raise RuntimeError if database is not connected.
        Called before every DB operation.
        """
        if not self._is_connected or self._database is None:
            raise RuntimeError(
                "Database is not connected. "
                "Call await db_manager.connect() first."
            )

    def _get_masked_host(self) -> str:
        """
        Extract and mask the MongoDB host from the URI.
        Safe for logging — never exposes credentials.
        """
        try:
            uri = settings.mongo_uri
            # Extract host part between @ and /
            if "@" in uri:
                host_part = uri.split("@")[1].split("/")[0]
                return host_part
            return "atlas-cluster"
        except Exception:
            return "unknown-host"

    def __repr__(self) -> str:
        return (
            f"DatabaseManager("
            f"connected={self._is_connected}, "
            f"db={settings.DB_NAME}"
            f")"
        )


# ============================================================
#   MODULE-LEVEL HELPERS
#   Convenience functions for direct collection access
# ============================================================

async def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active database instance.

    Usage:
        db = await get_database()
        await db.users.find_one({"user_id": 123})
    """
    return db_manager.database


async def get_collection(name: str) -> AsyncIOMotorCollection:
    """
    Return a collection by name directly.

    Usage:
        col = await get_collection(Collections.USERS)
        await col.insert_one({...})
    """
    return db_manager.get_collection(name)


# ============================================================
#   SINGLETON INSTANCE
#   Import this everywhere: from database.connection import db_manager
# ============================================================

db_manager = DatabaseManager()