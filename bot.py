import nest_asyncio
nest_asyncio.apply()

import difflib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from docx import Document

import os
TOKEN = os.getenv("TOKEN")
# المستخدمين المسموح لهم
ALLOWED_USERS = [
5635911252,872708926,7057742713,7835441428,1176367759,
8610835600,6551983032,6713486568,8513455319,5994226138,
8408377860,8683282271,8630649440,5693299704,947418368,
5374990356,7013506338,6503533159,1222786232,842237376,
2088189031,6652935483,1460026877,868074642,6907189160,
7259279718,8074207624,1755554203,8165550047,603447675,
7023646451,1239011091,1101653764,1724283096,8233670186,
7477502529,657056020,1283862924,6971925807,991156346,
6275481474,1499594313,2009912665,8009027408,6862452209,
1118604355,7517449018
]

def is_allowed(user_id):
    return user_id in ALLOWED_USERS

# -------- قراءة الوورد --------
def read_word_sections():

    doc = Document("info.docx")

    sections = {}
    current_title = "عام"

    sections[current_title] = {
        "title": current_title,
        "content": ""
    }

    for para in doc.paragraphs:

        text = para.text.strip()

        if not text:
            continue

        if "Heading" in para.style.name:
            current_title = text
            sections[current_title.lower()] = {
                "title": text,
                "content": ""
            }
        else:
            sections[current_title.lower()]["content"] += text + "\n"

    return sections

sections_data = read_word_sections()

user_choices = {}

# -------- start --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح لك")
        return

    await update.message.reply_text(
        "🤖 البوت شغال\n"
        "اكتب اسم القسم أو جزء منه\n"
        "أو /list لعرض الأقسام"
    )

# -------- عرض الأقسام --------
async def list_sections(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح لك")
        return

    message = "📚 الأقسام:\n\n"

    for key in sections_data:
        message += f"- {sections_data[key]['title']}\n"

    await update.message.reply_text(message[:4000])

# -------- البحث --------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح لك")
        return

    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    # اختيار رقم
    if user_id in user_choices and text.isdigit():

        index = int(text) - 1
        matches = user_choices[user_id]

        if 0 <= index < len(matches):

            section = sections_data[matches[index]]

            await update.message.reply_text(
                f"📌 {section['title']}\n\n{section['content']}"[:4000]
            )

            del user_choices[user_id]
            return

        else:
            await update.message.reply_text("❌ رقم غلط")
            return

    titles = list(sections_data.keys())

    matches = difflib.get_close_matches(text, titles, n=5, cutoff=0.3)

    if len(matches) == 1:

        section = sections_data[matches[0]]

        await update.message.reply_text(
            f"📌 {section['title']}\n\n{section['content']}"[:4000]
        )

    elif len(matches) > 1:

        user_choices[user_id] = matches

        message = "📌 اختر رقم القسم:\n\n"

        for i, match in enumerate(matches, 1):
            message += f"{i}- {sections_data[match]['title']}\n"

        await update.message.reply_text(message)

    else:

        await update.message.reply_text("❌ مش لاقي حاجة قريبة\nاكتب /list")

# -------- تشغيل البوت --------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list",list_sections))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🚀 البوت شغال...")

app.run_polling()
