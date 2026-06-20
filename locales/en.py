# ============================================================
#         StudyBuddyV3BOT — English Strings
#         All bot messages in English
#         Default language — fallback for all unsupported langs
# ============================================================

STRINGS = {

    # ================================================================
    #   GENERAL
    # ================================================================
    "welcome":              "👋 *Welcome to StudyBuddyV3BOT!*",
    "welcome_back":         "👋 *Welcome back, {name}!*",
    "main_menu":            "🚀 *Main Menu*\n\n_Select a feature below:_",
    "loading":              "⏳ _Loading..._",
    "processing":           "🔄 _Processing..._",
    "success":              "✅ *Done successfully!*",
    "error":                "❌ *An error occurred. Please try again.*",
    "cancelled":            "🚫 *Cancelled.*\n\n_Returning to main menu._",
    "unknown_command":      "⚠️ Unknown command. Use /start to begin.",
    "try_again":            "Please try again.",
    "back_to_menu":         "◀️ Back to Menu",
    "cancel":               "🚫 Cancel",
    "confirm":              "✔️ Confirm",
    "yes":                  "Yes",
    "no":                   "No",

    # ================================================================
    #   ONBOARDING
    # ================================================================
    "new_user_welcome": (
        "👋 *Welcome to StudyBuddyV3BOT!*\n"
        "{'─' * 35}\n\n"
        "Hello {name}! 👋\n\n"
        "I'm your personal AI-powered study assistant.\n\n"
        "🤖 *AI Assistant* — Ask me anything\n"
        "🧮 *Calculator* — Advanced math operations\n"
        "🌐 *Translator* — Translate text instantly\n"
        "📚 *Notes* — Save your study notes\n"
        "🌍 *Language* — Switch bot language\n\n"
        "_Tap a button below to get started!_ 🚀"
    ),
    "returning_user_welcome": (
        "👋 *Welcome back, {name}!*\n\n"
        "Good to see you again! 😊\n"
        "What would you like to do today?\n\n"
        "_Use the menu below to get started._"
    ),

    # ================================================================
    #   AI ASSISTANT
    # ================================================================
    "ai_menu": (
        "🤖 *AI Study Assistant*\n"
        "{'─' * 35}\n\n"
        "I'm your personal AI tutor powered by GPT-4o-mini.\n\n"
        "📚 *I can help you with:*\n"
        "  • Explaining concepts\n"
        "  • Solving problems\n"
        "  • Summarizing topics\n"
        "  • Answering questions\n"
        "  • Study tips & strategies\n\n"
        "_Just type your question or tap Ask below!_"
    ),
    "ai_ask_prompt": (
        "🤖 *Ask AI Study Assistant*\n"
        "{'─' * 35}\n\n"
        "📝 Type your question below and I'll answer it!\n\n"
        "_Examples:_\n"
        "• _What is photosynthesis?_\n"
        "• _Explain Newton's laws of motion_\n"
        "• _Summarize the French Revolution_"
    ),
    "ai_thinking":          "⏳ _Thinking..._",
    "ai_rate_limited": (
        "⚠️ *AI Rate Limit Reached*\n\n"
        "You've used your hourly AI request limit.\n"
        "⏳ Please wait `{wait_time}` seconds.\n\n"
        "_Limit: {limit} requests/hour_"
    ),
    "ai_error": (
        "❌ *Something went wrong*\n\n"
        "Could not get an AI response.\n"
        "Please try again."
    ),
    "ai_context_cleared": (
        "✅ *Conversation Cleared*\n\n"
        "Your AI conversation history has been reset.\n"
        "_Starting fresh — ask me anything!_"
    ),
    "ai_question_too_long": (
        "⚠️ Your question is too long.\n"
        "Please keep it under `{max}` characters."
    ),

    # ================================================================
    #   CALCULATOR
    # ================================================================
    "calc_title":           "🧮 *Calculator*",
    "calc_result":          "= {result}",
    "calc_error":           "⚠️ Error: {error}",
    "calc_too_long":        "Expression too long!",
    "calc_opened":          "🧮 Calculator opened",

    # ================================================================
    #   TRANSLATOR
    # ================================================================
    "translator_menu": (
        "🌐 *Text Translator*\n"
        "{'─' * 35}\n\n"
        "Translate any text to 100+ languages\n"
        "powered by Google Translate.\n\n"
        "*How to use:*\n"
        "  1️⃣ Tap *Translate Text*\n"
        "  2️⃣ Send the text you want to translate\n"
        "  3️⃣ Choose target language\n"
        "  4️⃣ Get instant translation!\n\n"
        "_Tap below to get started!_"
    ),
    "translator_prompt": (
        "🌐 *Translate Text*\n"
        "{'─' * 35}\n\n"
        "📝 Send the text you want to translate.\n\n"
        "📏 Max: `{max_length}` characters"
    ),
    "translator_choose_lang": (
        "🌍 *Choose Target Language*\n"
        "{'─' * 35}\n\n"
        "📝 *Your text:*\n"
        "_{preview}_\n\n"
        "🌍 Select the language to translate to:"
    ),
    "translator_result": (
        "🌐 *Translation Result*\n"
        "{'─' * 35}\n\n"
        "📝 *Original:*\n"
        "_{original}_\n\n"
        "🌍 *Translated to {lang}:*\n"
        "{translated}\n\n"
        "{'─' * 35}\n"
        "🔍 Detected: _{source_lang}_"
    ),
    "translator_error": (
        "❌ *Translation Failed*\n\n"
        "Could not translate to `{lang}`.\n"
        "Please try again."
    ),
    "translator_too_long": (
        "⚠️ Text too long.\n"
        "Max `{max}` characters.\n"
        "Your text: `{length}` characters."
    ),

    # ================================================================
    #   NOTES
    # ================================================================
    "notes_menu": (
        "📚 *Study Notes*\n"
        "{'─' * 35}\n\n"
        "📊 Notes: `{count}` / `{capacity}`\n\n"
        "_What would you like to do?_"
    ),
    "notes_save_prompt": (
        "💾 *Save New Note*\n"
        "{'─' * 35}\n\n"
        "📝 Send your note content now.\n\n"
        "📏 Max length: `{max_length}` characters\n\n"
        "_Tip: Start with a title on the first line!_"
    ),
    "notes_saved": (
        "✅ *Note Saved!*\n\n"
        "📝 Title: _{title}_\n"
        "📏 Length: `{length}` characters\n"
        "📊 Total Notes: `{count}` / `{capacity}`"
    ),
    "notes_list_title":     "📚 *My Notes* ({total} total)",
    "notes_empty": (
        "📭 You have no saved notes yet.\n\n"
        "_Tap 'Save Note' to create your first note!_"
    ),
    "notes_limit_reached": (
        "⚠️ *Notes Limit Reached*\n\n"
        "You have `{count}` / `{capacity}` notes.\n\n"
        "Please delete some notes before saving new ones."
    ),
    "notes_deleted":        "🗑️ Note deleted successfully.",
    "notes_all_deleted": (
        "✅ *All Notes Deleted*\n\n"
        "🗑️ Deleted `{count}` notes successfully."
    ),
    "notes_not_found":      "⚠️ Note not found or already deleted.",
    "notes_too_long": (
        "⚠️ Note is too long.\n"
        "Max `{max}` characters."
    ),
    "notes_delete_confirm": (
        "🗑️ *Delete Note?*\n\n"
        "📝 *{title}*\n\n"
        "_{preview}_\n\n"
        "⚠️ This action cannot be undone."
    ),
    "notes_delete_all_confirm": (
        "🗑️ *Delete ALL Notes?*\n\n"
        "⚠️ You are about to delete *{count} notes*.\n\n"
        "*This action cannot be undone!*"
    ),

    # ================================================================
    #   LANGUAGE
    # ================================================================
    "language_menu": (
        "🌍 *Language Settings*\n"
        "{'─' * 35}\n\n"
        "🌍 Current Language: {current}\n\n"
        "Select your preferred language below.\n"
        "The bot interface will switch immediately."
    ),
    "language_changed": (
        "✅ *Language Changed!*\n\n"
        "Language set to: {language}\n\n"
        "_The bot will now respond in English._"
    ),
    "language_already_set": "✅ Already set to this language!",

    # ================================================================
    #   ERRORS
    # ================================================================
    "error_generic": (
        "⚠️ Something went wrong. Please try again\n"
        "or use /start to return to the main menu."
    ),
    "error_banned": (
        "🔨 *You Have Been Banned*\n\n"
        "You have been banned from using this bot.\n"
        "If you think this is a mistake, contact support."
    ),
    "error_maintenance": (
        "🔧 *Bot Under Maintenance*\n\n"
        "{message}\n\n"
        "_Please try again later._"
    ),
    "error_rate_limited": (
        "⚠️ *Rate Limit Reached*\n\n"
        "You are sending messages too fast.\n"
        "Please wait `{wait_time}` seconds."
    ),
    "error_not_found":      "⚠️ The requested item was not found.",
    "error_invalid_input":  "⚠️ Invalid input. Please try again.",

    # ================================================================
    #   HELP
    # ================================================================
    "help_title":           "❓ *Help Guide — StudyBuddyV3BOT*",
    "help_ai":              "🤖 *AI Assistant* — Ask study questions",
    "help_calculator":      "🧮 *Calculator* — Math operations",
    "help_translator":      "🌐 *Translator* — Translate text",
    "help_notes":           "📚 *Notes* — Save study notes",
    "help_language":        "🌍 *Language* — Switch bot language",
    "help_commands": (
        "*Commands:*\n"
        "  /start /menu /help /cancel"
    ),
    "help_footer":          "_Everything works via inline buttons!_",

    # ================================================================
    #   ADMIN
    # ================================================================
    "admin_unauthorized":   "🔐 *Access Denied*\n\nAdmin access required.",
    "admin_panel_title":    "👑 *Admin Panel — StudyBuddyV3BOT*",
    "admin_broadcast_sent": "📢 Broadcast sent to `{count}` users.",
    "admin_user_banned":    "🔨 User `{user_id}` has been banned.",
    "admin_user_unbanned":  "🔓 User `{user_id}` has been unbanned.",
    "admin_maintenance_on": "🔧 Maintenance mode *enabled*.",
    "admin_maintenance_off":"✅ Maintenance mode *disabled*.",
}