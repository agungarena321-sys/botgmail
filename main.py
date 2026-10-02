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
    kb = [
        [InlineKeyboardButton("⚡ AMBIL TUGAS", callback_data="ambil_tugas")],
        [InlineKeyboardButton("📩 BEBAS RULES", callback_data="bebas"), InlineKeyboardButton("🔐 SETOR CAPTCHA", callback_data="captcha")],
        [InlineKeyboardButton("📧 Generator", callback_data="generator"), InlineKeyboardButton("📜 Aturan & Info", callback_data="aturan")],
        [InlineKeyboardButton("👥 Referral", callback_data="referral"), InlineKeyboardButton("💰 Dompet (Tarik Saldo)", callback_data="dompet")],
        [InlineKeyboardButton("📊 Riwayat", callback_data="riwayat"), InlineKeyboardButton("🆘 Bantuan", callback_data="bantuan")],
        [InlineKeyboardButton("🤖 Bot Nokos", url="https://t.me/nokos_bot")],
    ]
    return InlineKeyboardMarkup(kb)

def get_back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (update.effective_user.id,))
    conn.commit()
    await update.message.reply_text("WIB\nPilih Menu:", reply_markup=get_menu())

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "back_menu":
        await query.edit_message_text("WIB\nPilih Menu:", reply_markup=get_menu())

    elif data == "ambil_tugas":
        txt = "TUGAS AKTIF:\n1. Buat Gmail baru (manual)\n2. Format: email|password|recovery"
        await query.edit_message_text(txt, reply_markup=get_back_menu())

    elif data in ["bebas", "captcha"]:
        context.user_data["tipe"] = data
        await query.message.reply_text(f"Kirim data Gmail untuk {data.upper()} format:\nemail|password\nContoh: budi123@gmail.com|pass123")
        return ASK_EMAIL

    elif data == "dompet":
        c.execute("SELECT saldo FROM users WHERE id=?", (uid,))
        row = c.fetchone()
        saldo = row[0] if row else 0
        await query.edit_message_text(f"💰 Dompet: Rp {saldo}\nUntuk Tarik hubungi Admin. Payment DANA.", reply_markup=get_back_menu())

    elif data == "aturan":
        txt = (
            "📜 ATURAN & INFO UMUM\n\n"
            "1️⃣ Wajib logout email dari HP\n"
            "2️⃣ Jangan otak-atik akun jika sudah di setor\n"
            "3️⃣ No verif & No tap tap\n"
            "4️⃣ Dilarang mengganti password setelah di setor\n"
            "5️⃣ Ketauan curang = Banned/No payment\n"
            "6️⃣ Wajib hapus semua keamanan\n"
            "7️⃣ Review & pay estimasi 24-48 jam (senin - jumat)\n"
            "8️⃣ Hanya melayani payment via DANA\n\n"
            "❗ LARANGAN:\n"
            "• Email dot-trick (variasi titik) = DILARANG\n"
            "• Password SALAH = Banned"
        )
        await query.edit_message_text(txt, reply_markup=get_back_menu())

    elif data == "riwayat":
        c.execute("SELECT data, status, waktu FROM setoran WHERE user_id=? ORDER BY id DESC LIMIT 10", (uid,))
        rows = c.fetchall()
        txt = "Belum ada riwayat." if not rows else "\n".join([f"[{r[2]}] {r[0]} | {r[1]}" for r in rows])
        await query.edit_message_text(f"📊 Riwayat:\n{txt}", reply_markup=get_back_menu())

    else:
        await query.edit_message_text(f"Fitur {data} segera hadir.", reply_markup=get_back_menu())

    return ConversationHandler.END

async def setor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data_text = update.message.text
    tipe = context.user_data.get("tipe", "bebas")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO setoran (user_id, data, status, waktu) VALUES (?,?,?,?)", (uid, data_text, f"PENDING-{tipe}", waktu))
    conn.commit()
    await update.message.reply_text("✅ Berhasil disetor! Menunggu ACC Admin 24-48 jam.", reply_markup=get_menu())
    kb_admin = InlineKeyboardMarkup([[InlineKeyboardButton("✅ ACC +100
