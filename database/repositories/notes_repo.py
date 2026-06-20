# ============================================================
#         StudyBuddyV3BOT — Notes Repository
#         All database operations for the notes collection
#         Async Motor-based CRUD + pagination + search
# ============================================================

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from database.connection import db_manager
from database.models import NoteModel, utcnow_naive
from config.constants import Collections, NoteStatus, LimitConstants
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
#   NOTES REPOSITORY
# ============================================================

class NotesRepository:
    """
    Handles all database operations for the notes collection.

    Responsibilities:
    - Create / save notes
    - Fetch notes by user (with pagination)
    - Fetch single note by ID
    - Update note content
    - Soft-delete notes
    - Search notes by keyword
    - Count notes per user

    Usage:
        from database.repositories import notes_repo
        notes = await notes_repo.get_user_notes(user_id=12345)
    """

    def __init__(self) -> None:
        self._collection_name = Collections.NOTES

    @property
    def collection(self):
        """Return the notes collection from active DB connection."""
        return db_manager.get_collection(self._collection_name)

    # ================================================================
    #   CREATE
    # ================================================================

    async def create(
        self,
        user_id:  int,
        content:  str,
        title:    str = "",
        tags:     Optional[List[str]] = None,
    ) -> Optional[NoteModel]:
        """
        Create and save a new note for a user.

        Args:
            user_id: Owner's Telegram user ID
            content: Note body text
            title:   Optional note title
            tags:    Optional list of tags

        Returns:
            Created NoteModel or None on failure
        """
        try:
            # Generate unique note ID
            note_id = str(uuid.uuid4())

            note = NoteModel(
                note_id=  note_id,
                user_id=  user_id,
                title=    title.strip() if title else "",
                content=  content.strip(),
                tags=     tags or [],
            )

            await self.collection.insert_one(note.to_dict())

            logger.info(
                f"✅ Note created | "
                f"ID: {note_id[:8]} | "
                f"User: {user_id} | "
                f"Title: {note.display_title!r}"
            )
            return note

        except PyMongoError as e:
            logger.error(
                f"DB error creating note for user {user_id}: {e}"
            )
            return None

    # ================================================================
    #   READ / FETCH
    # ================================================================

    async def get_by_id(
        self,
        note_id: str,
        user_id: Optional[int] = None,
    ) -> Optional[NoteModel]:
        """
        Fetch a single note by its unique note_id.
        Optionally filter by user_id for ownership verification.

        Args:
            note_id: UUID string of the note
            user_id: Optional owner verification

        Returns:
            NoteModel if found and active, None otherwise
        """
        try:
            query: Dict[str, Any] = {
                "note_id": note_id,
                "status":  NoteStatus.ACTIVE.value,
            }

            # Add ownership check if user_id provided
            if user_id is not None:
                query["user_id"] = user_id

            doc = await self.collection.find_one(query)
            if doc:
                return NoteModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(f"DB error fetching note {note_id}: {e}")
            return None

    async def get_user_notes(
        self,
        user_id: int,
        skip:    int = 0,
        limit:   int = LimitConstants.NOTES_PER_PAGE,
    ) -> List[NoteModel]:
        """
        Fetch all active notes for a user with pagination.

        Args:
            user_id: Owner's Telegram user ID
            skip:    Number of documents to skip (for pagination)
            limit:   Max notes to return per page

        Returns:
            List of active NoteModel instances
        """
        try:
            cursor = (
                self.collection
                .find(
                    {
                        "user_id": user_id,
                        "status":  NoteStatus.ACTIVE.value,
                    }
                )
                .sort("created_at", -1)       # Newest first
                .skip(skip)
                .limit(limit)
            )

            docs = await cursor.to_list(length=limit)
            return [NoteModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error fetching notes for user {user_id}: {e}"
            )
            return []

    async def get_all_user_notes(
        self,
        user_id: int,
    ) -> List[NoteModel]:
        """
        Fetch ALL active notes for a user (no pagination).
        Used for export or bulk operations.

        Args:
            user_id: Owner's Telegram user ID

        Returns:
            Complete list of active NoteModel instances
        """
        try:
            cursor = self.collection.find(
                {
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                }
            ).sort("created_at", -1)

            docs = await cursor.to_list(length=None)
            return [NoteModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error fetching all notes for user {user_id}: {e}"
            )
            return []

    async def search_notes(
        self,
        user_id: int,
        keyword: str,
        limit:   int = 10,
    ) -> List[NoteModel]:
        """
        Search a user's notes by keyword in title or content.
        Case-insensitive full-text search using regex.

        Args:
            user_id: Owner's Telegram user ID
            keyword: Search term
            limit:   Max results to return

        Returns:
            List of matching NoteModel instances
        """
        try:
            # Escape special regex characters in keyword
            import re
            escaped = re.escape(keyword.strip())

            cursor = self.collection.find(
                {
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                    "$or": [
                        {
                            "title": {
                                "$regex":   escaped,
                                "$options": "i",    # Case-insensitive
                            }
                        },
                        {
                            "content": {
                                "$regex":   escaped,
                                "$options": "i",
                            }
                        },
                        {
                            "tags": {
                                "$regex":   escaped,
                                "$options": "i",
                            }
                        },
                    ],
                }
            ).sort("created_at", -1).limit(limit)

            docs = await cursor.to_list(length=limit)
            return [NoteModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error searching notes for user {user_id}: {e}"
            )
            return []

    async def get_recent_notes(
        self,
        user_id: int,
        limit:   int = 3,
    ) -> List[NoteModel]:
        """
        Fetch the most recently created notes for a user.
        Used for quick-access previews in the notes menu.

        Args:
            user_id: Owner's Telegram user ID
            limit:   Number of recent notes to return

        Returns:
            List of most recent NoteModel instances
        """
        try:
            cursor = (
                self.collection
                .find(
                    {
                        "user_id": user_id,
                        "status":  NoteStatus.ACTIVE.value,
                    }
                )
                .sort("created_at", -1)
                .limit(limit)
            )

            docs = await cursor.to_list(length=limit)
            return [NoteModel.from_dict(d) for d in docs]

        except PyMongoError as e:
            logger.error(
                f"DB error fetching recent notes for user {user_id}: {e}"
            )
            return []

    async def get_notes_page(
        self,
        user_id:  int,
        page:     int = 1,
        per_page: int = LimitConstants.NOTES_PER_PAGE,
    ) -> Dict[str, Any]:
        """
        Fetch a paginated page of notes with metadata.
        Returns both the notes and pagination info.

        Args:
            user_id:  Owner's Telegram user ID
            page:     Page number (1-based)
            per_page: Notes per page

        Returns:
            Dict with notes, page, total_pages, total_count, has_next, has_prev
        """
        try:
            # Total count for pagination math
            total = await self.count_user_notes(user_id)
            total_pages = max(1, -(-total // per_page))  # Ceiling division

            # Clamp page to valid range
            page = max(1, min(page, total_pages))
            skip = (page - 1) * per_page

            notes = await self.get_user_notes(
                user_id=user_id,
                skip=skip,
                limit=per_page,
            )

            return {
                "notes":       notes,
                "page":        page,
                "per_page":    per_page,
                "total":       total,
                "total_pages": total_pages,
                "has_next":    page < total_pages,
                "has_prev":    page > 1,
            }

        except Exception as e:
            logger.error(
                f"Error fetching notes page for user {user_id}: {e}"
            )
            return {
                "notes":       [],
                "page":        1,
                "per_page":    per_page,
                "total":       0,
                "total_pages": 1,
                "has_next":    False,
                "has_prev":    False,
            }

    # ================================================================
    #   UPDATE
    # ================================================================

    async def update(
        self,
        note_id: str,
        user_id: int,
        updates: Dict[str, Any],
    ) -> Optional[NoteModel]:
        """
        Generic update method for a note.
        Verifies ownership via user_id before updating.

        Args:
            note_id: UUID of the note to update
            user_id: Owner verification
            updates: Fields to update

        Returns:
            Updated NoteModel or None if not found
        """
        try:
            updates["updated_at"] = utcnow_naive()

            doc = await self.collection.find_one_and_update(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )

            if doc:
                return NoteModel.from_dict(doc)
            return None

        except PyMongoError as e:
            logger.error(f"DB error updating note {note_id}: {e}")
            return None

    async def update_content(
        self,
        note_id:  str,
        user_id:  int,
        content:  str,
        title:    Optional[str] = None,
    ) -> Optional[NoteModel]:
        """
        Update the content (and optionally title) of a note.

        Args:
            note_id: UUID of the note
            user_id: Owner verification
            content: New note body text
            title:   New title (optional — only updated if provided)

        Returns:
            Updated NoteModel or None
        """
        updates: Dict[str, Any] = {
            "content": content.strip(),
        }
        if title is not None:
            updates["title"] = title.strip()

        return await self.update(note_id, user_id, updates)

    async def add_tag(
        self,
        note_id: str,
        user_id: int,
        tag:     str,
    ) -> bool:
        """
        Add a tag to a note (if not already present).

        Args:
            note_id: UUID of the note
            user_id: Owner verification
            tag:     Tag string to add

        Returns:
            True if tag added successfully
        """
        try:
            result = await self.collection.update_one(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                {
                    "$addToSet": {"tags": tag.lower().strip()},
                    "$set":      {"updated_at": utcnow_naive()},
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(f"DB error adding tag to note {note_id}: {e}")
            return False

    async def remove_tag(
        self,
        note_id: str,
        user_id: int,
        tag:     str,
    ) -> bool:
        """
        Remove a tag from a note.

        Args:
            note_id: UUID of the note
            user_id: Owner verification
            tag:     Tag string to remove

        Returns:
            True if tag removed successfully
        """
        try:
            result = await self.collection.update_one(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                {
                    "$pull": {"tags": tag.lower().strip()},
                    "$set":  {"updated_at": utcnow_naive()},
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error removing tag from note {note_id}: {e}"
            )
            return False

    # ================================================================
    #   DELETE (SOFT)
    # ================================================================

    async def delete(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:
        """
        Soft-delete a note by setting status to 'deleted'.
        The note remains in the database but is invisible to the user.
        Ownership is verified via user_id.

        Args:
            note_id: UUID of the note to delete
            user_id: Owner's Telegram user ID (for verification)

        Returns:
            True if deleted successfully, False if not found
        """
        try:
            result = await self.collection.update_one(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                {
                    "$set": {
                        "status":     NoteStatus.DELETED.value,
                        "deleted_at": utcnow_naive(),
                        "updated_at": utcnow_naive(),
                    }
                },
            )

            success = result.modified_count > 0
            if success:
                logger.info(
                    f"🗑️  Note soft-deleted | "
                    f"ID: {note_id[:8]} | "
                    f"User: {user_id}"
                )
            return success

        except PyMongoError as e:
            logger.error(
                f"DB error deleting note {note_id} "
                f"for user {user_id}: {e}"
            )
            return False

    async def delete_all_user_notes(self, user_id: int) -> int:
        """
        Soft-delete ALL notes for a user.
        Used when a user requests to clear all their notes.

        Args:
            user_id: Owner's Telegram user ID

        Returns:
            Number of notes deleted
        """
        try:
            result = await self.collection.update_many(
                {
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                {
                    "$set": {
                        "status":     NoteStatus.DELETED.value,
                        "deleted_at": utcnow_naive(),
                        "updated_at": utcnow_naive(),
                    }
                },
            )

            count = result.modified_count
            if count > 0:
                logger.info(
                    f"🗑️  Bulk delete | "
                    f"User: {user_id} | "
                    f"Deleted: {count} notes"
                )
            return count

        except PyMongoError as e:
            logger.error(
                f"DB error bulk deleting notes for user {user_id}: {e}"
            )
            return 0

    async def restore(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:
        """
        Restore a soft-deleted note back to active status.

        Args:
            note_id: UUID of the note to restore
            user_id: Owner verification

        Returns:
            True if restored successfully
        """
        try:
            result = await self.collection.update_one(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.DELETED.value,
                },
                {
                    "$set": {
                        "status":     NoteStatus.ACTIVE.value,
                        "deleted_at": None,
                        "updated_at": utcnow_naive(),
                    }
                },
            )
            return result.modified_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error restoring note {note_id}: {e}"
            )
            return False

    async def hard_delete(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:
        """
        Permanently delete a note from the database.
        Use only when necessary — prefer soft delete.

        Args:
            note_id: UUID of the note
            user_id: Owner verification

        Returns:
            True if permanently deleted
        """
        try:
            result = await self.collection.delete_one(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                }
            )
            return result.deleted_count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error hard-deleting note {note_id}: {e}"
            )
            return False

    # ================================================================
    #   COUNT / STATISTICS
    # ================================================================

    async def count_user_notes(self, user_id: int) -> int:
        """
        Count total active notes for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            Integer count of active notes
        """
        try:
            return await self.collection.count_documents(
                {
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                }
            )
        except PyMongoError as e:
            logger.error(
                f"DB error counting notes for user {user_id}: {e}"
            )
            return 0

    async def user_has_capacity(self, user_id: int) -> bool:
        """
        Check if a user can save more notes (under the limit).

        Args:
            user_id: Telegram user ID

        Returns:
            True if user has capacity to save more notes
        """
        count = await self.count_user_notes(user_id)
        return count < LimitConstants.MAX_NOTES_PER_USER

    async def get_total_notes_count(self) -> int:
        """
        Return total number of active notes across all users.
        Used in admin stats panel.

        Returns:
            Integer count of all active notes
        """
        try:
            return await self.collection.count_documents(
                {"status": NoteStatus.ACTIVE.value}
            )
        except PyMongoError as e:
            logger.error(f"DB error counting total notes: {e}")
            return 0

    async def get_notes_stats(self) -> Dict[str, Any]:
        """
        Return notes statistics for the admin panel.

        Returns:
            Dict with total_active, total_deleted, total_all
        """
        try:
            total_active = await self.collection.count_documents(
                {"status": NoteStatus.ACTIVE.value}
            )
            total_deleted = await self.collection.count_documents(
                {"status": NoteStatus.DELETED.value}
            )

            return {
                "total_active":  total_active,
                "total_deleted": total_deleted,
                "total_all":     total_active + total_deleted,
            }

        except PyMongoError as e:
            logger.error(f"DB error getting notes stats: {e}")
            return {
                "total_active":  0,
                "total_deleted": 0,
                "total_all":     0,
            }

    async def exists(
        self,
        note_id: str,
        user_id: int,
    ) -> bool:
        """
        Check if an active note exists for a given user.

        Args:
            note_id: UUID of the note
            user_id: Owner verification

        Returns:
            True if note exists and is active
        """
        try:
            count = await self.collection.count_documents(
                {
                    "note_id": note_id,
                    "user_id": user_id,
                    "status":  NoteStatus.ACTIVE.value,
                },
                limit=1,
            )
            return count > 0

        except PyMongoError as e:
            logger.error(
                f"DB error checking note existence {note_id}: {e}"
            )
            return False
