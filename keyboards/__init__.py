# ============================================================
#         StudyBuddyV3BOT — Keyboards Package Init
#         Exposes all keyboard builder classes
#         at package level for clean imports
# ============================================================

from keyboards.main_menu      import MainMenuKeyboard
from keyboards.calculator_kb  import CalculatorKeyboard
from keyboards.language_kb    import LanguageKeyboard
from keyboards.notes_kb       import NotesKeyboard
from keyboards.translator_kb  import TranslatorKeyboard
from keyboards.admin_kb       import AdminKeyboard

__all__ = [
    # ── Keyboard Builders ──
    "MainMenuKeyboard",     # Main menu + feature entry points
    "CalculatorKeyboard",   # Full inline calculator button layout
    "LanguageKeyboard",     # Language selection + confirmation
    "NotesKeyboard",        # Notes list, detail, delete confirm
    "TranslatorKeyboard",   # Translator menu + language picker
    "AdminKeyboard",        # Admin panel navigation + actions
]