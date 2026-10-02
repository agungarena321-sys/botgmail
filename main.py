import sqlite3, requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = '8914843920:AAElvXYtPOEKAKmVxrhNWdzSeQA4BS2dn5U'
ADMIN_ID = 6523631884
ASK_EMAIL = 1

conn = sqlite3.connect('jobgmail.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, saldo INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS setoran (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, data TEXT, status TEXT, waktu TEXT)')
conn.commit()

def get_sholat():
    try:
        r = requests.get('https://api.aladhan.com/v1/timingsByCity?city=Semarang&country=Indonesia&method=20', timeout=5).json()
        t = r['data']['timings']
        return f"🕌 *JADWAL SHOLAT SEMARANG - {datetime.now().strftime('%d %b %Y')}*\n" \
               f"🌙 Subuh: {t['Fajr']} | ☀️ Dzuhur: {t['Dhuhr']}\n" \
               f"🌤️ Ashar: {t['Asr']} | 🌇 Maghrib: {t['Maghrib']} | 🌃 Isya: {t['Isha']}\n" \
               f"━━━━━━━━━━━━━━━━━━"
    except:
        return f"🕌 *JADWAL SHOLAT SEMARANG - {datetime.now().strftime('%d %b %Y')}*\n" \
               f"🌙 Subuh: 04:06 | ☀️ Dzuhur: 11:31 | 🌤️ Ashar: 14:36\n" \
               f"🌇 Maghrib: 17:35 | 🌃 Isya: 18:44\n━━━━━━━━━━━━━━━━━━"

def get_menu():
    kb = [
        [InlineKeyboardButton('📥 AMBIL TUGAS', callback_data='ambil_tugas')],
        [InlineKeyboardButton('🔓 BEBAS RULES', callback_data='bebas'), InlineKeyboardButton('🤖 SETOR CAPTCHA', callback_data='captcha')],
        [InlineKeyboardButton('⚙️ Generator', callback_data='generator'), InlineKeyboardButton('📜 Aturan & Info', callback_data='aturan')],
        [InlineKeyboardButton('👥 Referral', callback_data='referral'), InlineKeyboardButton('💰 Dompet', callback_data='dompet')],
        [InlineKeyboardButton('📊 Riwayat', callback_data='riwayat'), InlineKeyboardButton('🆘 Bantuan', callback_data='bantuan')],
        [InlineKeyboardButton('🤖 Bot Nokos', url='https://t.me/nokos_bot')],
    ]
    return InlineKeyboardMarkup(kb)

def get_back():
    return InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Kembali ke Menu', callback_data='back_menu')]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (update.effective_user.id,))
    conn.commit()
    sholat = get_sholat()
    txt = f"{sholat}\n\n⏰ *WIB {datetime.now().strftime('%H:%M')}* - Semarang\n👋 Halo, Pilih Menu di bawah:"
    await update.message.reply_text(txt, reply_markup=get_menu(), parse_mode='Markdown')

async def ask_bebas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data['tipe'] = q.data
    await q.message.reply_text(f"📩 Kirim data *{q.data.upper()}* format:\n`email|password`\nContoh: `budi123@gmail.com|pass123`", parse_mode='Markdown')
    return ASK_EMAIL

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id
    if data == 'back_menu':
        sholat = get_sholat()
        await q.edit_message_text(f"{sholat}\n\n⏰ *WIB {datetime.now().strftime('%H:%M')}* - Semarang\nPilih Menu:", reply_markup=get_menu(), parse_mode='Markdown')
    elif data == 'aturan':
        txt = "📜 *ATURAN & INFO UMUM*\n\n1️⃣ Wajib logout email dari HP\n2️⃣ Jangan otak-atik akun jika sudah di setor\n3️⃣ No verif & No tap tap\n4️⃣ Dilarang ganti password setelah di setor\n5️⃣ Ketauan curang = Banned/No payment\n6️⃣ Wajib hapus semua keamanan\n7️
