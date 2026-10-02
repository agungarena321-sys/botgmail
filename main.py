import sqlite3
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8914843920:AAFvFUul2yvr_dQyF_40_rfSKmCMeKSRIdQ"
ADMIN_ID = 6523631884
ASK_EMAIL = 1

conn = sqlite3.connect("jobgmail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, saldo INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS setoran (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, data TEXT, status TEXT, waktu TEXT)")
conn.commit()

def get_menu():
    keyboard = [
        [InlineKeyboardButton("⚡ AMBIL TUGAS", callback_data='ambil_tugas')],
        [InlineKeyboardButton("📩 BEBAS RULES", callback_data='bebas'), InlineKeyboardButton("🧩 SETOR CAPTCHA", callback_data='captcha')],
        [InlineKeyboardButton("🎲 Generator", callback_data='generator'), InlineKeyboardButton("ℹ️ Aturan & Info", callback_data='aturan')],
        [InlineKeyboardButton("🤝 Referral", callback_data='referral'), InlineKeyboardButton("💳 Dompet (Tarik Saldo)", callback_data='dompet')],
        [InlineKeyboardButton("📊 Riwayat", callback_data='riwayat'), InlineKeyboardButton("💬 Bantuan", callback_data='bantuan')],
        [InlineKeyboardButton("Bot Nokos 🤖", url="https://t.me/nokos_bot")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    text = f"Panduan Menu:\n📩 Bebas Rules: Setor Gmail tanpa rules ketat.\n🧩 Setor Captcha: Setor akun Captcha.\n\n⏰ Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB\nPilih Menu:"
    await update.message.reply_text(text, reply_markup=get_menu())

# ... (lengkap seperti file yang aku buat)