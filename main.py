from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

checklist_items = [
    "Site clear of hazards",
    "Equipment handed over",
    "Briefing conducted",
    "Logbook signed"
]
user_progress = {}

def get_checklist_keyboard(user_id):
    user_data = user_progress.get(user_id, [False] * len(checklist_items))
    keyboard = []
    for i, item in enumerate(checklist_items):
        status = "✅" if user_data[i] else "❌"
        keyboard.append([InlineKeyboardButton(f"{status} {item}", callback_data=str(i))])
    return InlineKeyboardMarkup(keyboard)

async def start_handover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = [False] * len(checklist_items)
    await update.message.reply_text(
        "🔄 Handing Over Checklist:\nClick to mark items completed.",
        reply_markup=get_checklist_keyboard(user_id)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    index = int(query.data)
    user_data = user_progress.get(user_id, [False] * len(checklist_items))
    user_data[index] = not user_data[index]
    user_progress[user_id] = user_data

    await query.edit_message_text(
        text="🔄 Handing Over Checklist:\nClick to mark items completed.",
        reply_markup=get_checklist_keyboard(user_id)
    )
    if all(user_data):
        await query.message.reply_text(
            f"✅ All items completed by {query.from_user.first_name} at {query.message.date}."
        )

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("handover", start_handover))
app.add_handler(CallbackQueryHandler(button_handler))

print("🤖 HOTO Bot running...")
app.run_polling()
