# ============================================================
#         StudyBuddyV3BOT — Calculator Keyboard
#         Full inline button calculator layout
#         Scientific calculator UI with all operations
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EmojiConstants


# ============================================================
#   CALCULATOR KEYBOARD
# ============================================================

class CalculatorKeyboard:
    """
    Builds the inline calculator button layout.

    Layout:
    - Row 1: AC, +/-, %, ÷
    - Row 2: 7, 8, 9, ×
    - Row 3: 4, 5, 6, -
    - Row 4: 1, 2, 3, +
    - Row 5: 0, ., ⌫, =
    - Row 6: Scientific ops (sqrt, sq, sin, cos)
    - Row 7: Scientific ops (tan, log, ln, π, e)
    - Row 8: Brackets + back button
    """

    @staticmethod
    def calculator(expr: str = "") -> InlineKeyboardMarkup:
        """
        Build the full calculator keyboard.
        Layout mirrors a real scientific calculator.

        Args:
            expr: Current expression (used to determine AC vs C)
        """

        # Determine clear button label
        clear_label = "C" if expr else "AC"

        def btn(label: str, action: str, value: str = "") -> InlineKeyboardButton:
            """Helper to build a calculator button."""
            if value:
                callback = f"calc:{action}:{value}"
            else:
                callback = f"calc:{action}"
            return InlineKeyboardButton(text=label, callback_data=callback)

        buttons = [

            # ── Row 1: Clear, Sign, Percent, Divide ──
            [
                btn(clear_label,  "clear_all" if not expr else "clear"),
                btn("+/-",        "sign"),
                btn("%",          "digit",   "%"),
                btn("÷",          "digit",   "/"),
            ],

            # ── Row 2: 7, 8, 9, Multiply ──
            [
                btn("7",   "digit", "7"),
                btn("8",   "digit", "8"),
                btn("9",   "digit", "9"),
                btn("×",   "digit", "*"),
            ],

            # ── Row 3: 4, 5, 6, Subtract ──
            [
                btn("4",   "digit", "4"),
                btn("5",   "digit", "5"),
                btn("6",   "digit", "6"),
                btn("-",   "digit", "-"),
            ],

            # ── Row 4: 1, 2, 3, Add ──
            [
                btn("1",   "digit", "1"),
                btn("2",   "digit", "2"),
                btn("3",   "digit", "3"),
                btn("+",   "digit", "+"),
            ],

            # ── Row 5: 0, Decimal, Backspace, Equals ──
            [
                btn("0",   "digit",     "0"),
                btn(".",   "decimal"),
                btn("⌫",   "backspace"),
                btn("=",   "equals"),
            ],

            # ── Row 6: Scientific — sqrt, x², sin, cos ──
            [
                btn("√",    "op",  "sqrt"),
                btn("x²",   "op",  "sq"),
                btn("sin",  "op",  "sin"),
                btn("cos",  "op",  "cos"),
            ],

            # ── Row 7: Scientific — tan, log, ln, π, e ──
            [
                btn("tan",  "op",  "tan"),
                btn("log",  "op",  "log"),
                btn("ln",   "op",  "ln"),
                btn("π",    "op",  "pi"),
                btn("e",    "op",  "e"),
            ],

            # ── Row 8: Brackets + Power + Back ──
            [
                btn("(",    "digit",  "("),
                btn(")",    "digit",  ")"),
                btn("xⁿ",   "op",     "pow"),
                btn("1/x",  "op",     "inv"),
                btn(
                    f"{EmojiConstants.BACK}",
                    "back"
                ),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def simple_calculator() -> InlineKeyboardMarkup:
        """
        Build a simplified calculator keyboard.
        Basic operations only — no scientific functions.
        Used as fallback for small screens.
        """

        def btn(label: str, action: str, value: str = "") -> InlineKeyboardButton:
            callback = f"calc:{action}:{value}" if value else f"calc:{action}"
            return InlineKeyboardButton(text=label, callback_data=callback)

        buttons = [
            # Row 1: AC, %, ÷
            [
                btn("AC",  "clear_all"),
                btn("%",   "digit",   "%"),
                btn("⌫",   "backspace"),
                btn("÷",   "digit",   "/"),
            ],
            # Row 2: 7, 8, 9, ×
            [
                btn("7",   "digit",   "7"),
                btn("8",   "digit",   "8"),
                btn("9",   "digit",   "9"),
                btn("×",   "digit",   "*"),
            ],
            # Row 3: 4, 5, 6, -
            [
                btn("4",   "digit",   "4"),
                btn("5",   "digit",   "5"),
                btn("6",   "digit",   "6"),
                btn("-",   "digit",   "-"),
            ],
            # Row 4: 1, 2, 3, +
            [
                btn("1",   "digit",   "1"),
                btn("2",   "digit",   "2"),
                btn("3",   "digit",   "3"),
                btn("+",   "digit",   "+"),
            ],
            # Row 5: 0, ., =, Back
            [
                btn("0",   "digit",   "0"),
                btn(".",   "decimal"),
                btn("=",   "equals"),
                btn(f"{EmojiConstants.BACK}", "back"),
            ],
        ]

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def error_keyboard() -> InlineKeyboardMarkup:
        """
        Build keyboard shown after a calculation error.
        Offers clear and back options.
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text=          "🔄 Try Again",
                    callback_data= "calc:clear_all",
                ),
                InlineKeyboardButton(
                    text=          f"{EmojiConstants.BACK} Menu",
                    callback_data= "calc:back",
                ),
            ]
        ]
        return InlineKeyboardMarkup(buttons)