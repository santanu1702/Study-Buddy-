# ============================================================
#         StudyBuddyV3BOT — Notes Keyboard
#         All inline keyboards for the notes feature
#         List, detail, delete confirm, pagination
# ============================================================

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EmojiConstants, LimitConstants
from database.models import NoteModel


# ============================================================
#   NOTES KEYBOARD
# ============================================================

class NotesKeyboard:
    """
    Builds all inline keyboards for the notes feature.

    Keyboards:
    - notes_menu:          Main notes menu buttons
    - notes_list:          Paginated notes list with buttons
    - note_detail:         Single note view with actions
    - delete_confirm:      Single note delete confirmation
    - delete_all_confirm:  Delete all notes confirmation
    - after_save:          Buttons shown after saving a note
    - empty_notes:         Shown when user has no notes
    - back_to_menu:        Single back to notes menu button
    - cancel_button:       Single cancel button
    """

    # ================================================================
    #   NOTES MENU
    # ================================================================

    @staticmethod
    def notes_menu(has_notes: bool = False) -> InlineKeyboardMarkup:
        """
        Build the main notes menu keyboard.

        Args:
            has_notes: Whether user has any saved notes
        """
        buttons = [
            # Row 1: Save Note
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.SAVE} Save Note",
                    callback_data= "notes:save",
                ),
            ],
        ]

        # Only show view/delete options if user has notes
        if has_notes:
            buttons.append([
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.VIEW} View Notes",
                    callback_data= "notes:list:1",
                ),
            ])
            buttons.append([
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Delete All",
                    callback_data= "notes:delete_all",
                ),
            ])

        # Back to main menu
        buttons.append([
            InlineKeyboardButton(
                text=          f"{EmojiConstants.BACK} Main Menu",
                callback_data= "menu:main",
            ),
        ])

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   NOTES LIST (PAGINATED)
    # ================================================================

    @staticmethod
    def notes_list(
        notes:       List[NoteModel],
        page:        int = 1,
        total_pages: int = 1,
        has_next:    bool = False,
        has_prev:    bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Build the paginated notes list keyboard.
        Each note gets its own button row.
        Navigation arrows at bottom.

        Args:
            notes:       List of NoteModel for current page
            page:        Current page number (1-based)
            total_pages: Total number of pages
            has_next:    Whether there is a next page
            has_prev:    Whether there is a previous page
        """
        buttons = []

        # ── Note buttons (one per note) ──
        for note in notes:
            # Truncate title for button label
            title = note.display_title
            if len(title) > 30:
                title = title[:27] + "..."

            buttons.append([
                InlineKeyboardButton(
                    text=          f"📄 {title}",
                    callback_data= f"notes:view:{note.note_id}",
                ),
            ])

        # ── Pagination row ──
        nav_row = []

        if has_prev:
            nav_row.append(
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Prev",
                    callback_data= f"notes:page:{page - 1}",
                )
            )

        # Page indicator (non-clickable)
        nav_row.append(
            InlineKeyboardButton(
                text=          f"📄 {page}/{total_pages}",
                callback_data= "calc:noop",     # No-op button
            )
        )

        if has_next:
            nav_row.append(
                InlineKeyboardButton(
                    text=          f"Next {EmojiConstants.NEXT}",
                    callback_data= f"notes:page:{page + 1}",
                )
            )

        if nav_row:
            buttons.append(nav_row)

        # ── Action row ──
        buttons.append([
            InlineKeyboardButton(
                text=          f"{EmojiConstants.SAVE} New Note",
                callback_data= "notes:save",
            ),
            InlineKeyboardButton(
                text=          f"{EmojiConstants.BACK} Menu",
                callback_data= "notes:back",
            ),
        ])

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   NOTE DETAIL
    # ================================================================

    @staticmethod
    def note_detail(note_id: str) -> InlineKeyboardMarkup:
        """
        Build the action keyboard for a single note detail view.

        Args:
            note_id: UUID of the note being viewed
        """
        buttons = [
            # Row 1: Delete button
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Delete Note",
                    callback_data= f"notes:delete:{note_id}",
                ),
            ],
            # Row 2: Back to list + Menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Back to List",
                    callback_data= "notes:back_list",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.ROCKET} Menu",
                    callback_data= "menu:main",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   DELETE CONFIRMATION
    # ================================================================

    @staticmethod
    def delete_confirm(note_id: str) -> InlineKeyboardMarkup:
        """
        Build confirmation keyboard for deleting a single note.

        Args:
            note_id: UUID of the note to be deleted
        """
        buttons = [
            [
                # Confirm delete
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.DELETE} Yes, Delete",
                    callback_data= f"notes:delete_confirm:{note_id}",
                ),
                # Cancel
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= f"notes:view:{note_id}",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def delete_all_confirm() -> InlineKeyboardMarkup:
        """
        Build confirmation keyboard for deleting ALL notes.
        Extra warning styling — destructive action.
        """
        buttons = [
            # Row 1: Confirm (dangerous)
            [
                InlineKeyboardButton(
                    text=          f"⚠️ Yes, Delete ALL",
                    callback_data= "notes:delete_all_confirm",
                ),
            ],
            # Row 2: Cancel (safe)
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel — Keep Notes",
                    callback_data= "notes:back",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   AFTER SAVE
    # ================================================================

    @staticmethod
    def after_save() -> InlineKeyboardMarkup:
        """
        Build keyboard shown after successfully saving a note.
        Quick actions: save another, view notes, or go home.
        """
        buttons = [
            # Row 1: Save another + View notes
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.SAVE} Save Another",
                    callback_data= "notes:save",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.VIEW} View Notes",
                    callback_data= "notes:list:1",
                ),
            ],
            # Row 2: Back to main menu
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Main Menu",
                    callback_data= "menu:main",
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    # ================================================================
    #   EMPTY NOTES
    # ================================================================

    @staticmethod
    def empty_notes() -> InlineKeyboardMarkup:
        """
        Build keyboard shown when user has no notes.
        Encourages saving first note.
        """
        buttons = [
            # Row 1: Save first note
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.SAVE} Save My First Note",
                    callback_data= "notes:save",
                ),
            ],
            # Row 2: Back to menu
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
    def back_to_menu() -> InlineKeyboardMarkup:
        """Single button — back to notes menu."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Notes Menu",
                    callback_data= "notes:back",
                ),
            ]
        ])

    @staticmethod
    def back_to_list() -> InlineKeyboardMarkup:
        """Single button — back to notes list."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Back to List",
                    callback_data= "notes:back_list",
                ),
            ]
        ])

    @staticmethod
    def cancel_button() -> InlineKeyboardMarkup:
        """Single cancel button — used during note input."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.CANCEL} Cancel",
                    callback_data= "notes:cancel",
                ),
            ]
        ])