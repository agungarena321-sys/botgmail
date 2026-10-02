import sqlite3
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8914846320:AAFvFuI2yvr_dQyF_40_rfSKmCMeKSRIdQ"
ADMIN_ID = 6523631884
ASK_EMAIL = 1

conn = sqlite3.connect("jobgmail.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, saldo INTEGER DEFAULT 0)")
c.execute("CREATE TABLE IF NOT EXISTS setoran (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, data TEXT, status TEXT, waktu TEXT)")
conn.commit()

def get_menu():
    kb = [
        [InlineKeyboardButton("AMBIL TUGAS", callback_data="ambil_tugas")],
        [InlineKeyboardButton("BEBAS RULES", callback_data="bebas"), InlineKeyboardButton("SETOR CAPTCHA", callback_data="captcha")],
        [InlineKeyboardButton("Generator", callback_data="generator"), InlineKeyboardButton("Aturan & Info", callback_data="aturan")],
        [InlineKeyboardButton("Referral", callback_data="referral"), InlineKeyboardButton("Dompet", callback_data="dompet")],
        [InlineKeyboardButton("Riwayat", callback_data="riwayat"), InlineKeyboardButton("Bantuan", callback_data="bantuan")],
    ]
    return InlineKeyboardMarkup(kb)

def get_back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Kembali ke Menu", callback_data="back_menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (update.effective_user.id,))
    conn.commit()
    await update.message.reply_text("WIB\nPilih Menu:", reply_markup=get_menu())

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id
    if data == "back_menu":
        await q.edit_message_text("WIB\nPilih Menu:", reply_markup=get_menu())
    elif data == "aturan":
        txt = "ATURAN & INFO UMUM\n\n1. Wajib logout email dari HP\n2. Jangan otak-atik akun jika sudah di setor\n3. No verif & No tap tap\n4. Dilarang ganti password setelah di setor\n5. Ketauan curang = Banned/No payment\n6. Wajib hapus semua keamanan\n7. Review & pay 24-48 jam (senin-jumat)\n8. Hanya payment via DANA\n\nLARANGAN:\n- Email dot-trick = DILARANG\n- Password SALAH = Banned"
        await q.edit_message_text(txt, reply_markup=get_back())
    elif data == "dompet":
        c.execute("SELECT saldo FROM users WHERE id=?", (uid,))
        r = c.fetchone()
        await q.edit_message_text(f"Dompet: Rp {r[0] if r else 0}", reply_markup=get_back())
    elif data == "riwayat":
        c.execute("SELECT data, status, waktu FROM setoran WHERE user_id=? ORDER BY id DESC LIMIT 10", (uid,))
        rows = c.fetchall()
        txt = "Belum ada riwayat." if not rows else "\n".join([f"{r[2]} {r[0]} {r[1]}" for r in rows])
        await q.edit_message_text(f"Riwayat:\n{txt}", reply_markup=get_back())
    elif data in ["bebas", "captcha"]:
        context.user_data["tipe"] = data
        await q.message.reply_text(f"Kirim data {data.upper()} format: email|password")
        return ASK_EMAIL
    else:
        await q.edit_message_text(f"Fitur {data} segera hadir.", reply_markup=get_back())
    return ConversationHandler.END

async def setor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO setoran (user_id, data, status, waktu) VALUES (?,?,?,?)", (uid, update.message.text, "PENDING", waktu))
    conn.commit()
    lid = c.lastrowid
    await update.message.reply_text("Berhasil disetor!", reply_markup=get_menu())
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(text="ACC", callback_data=f"acc_{uid}_{lid}"), InlineKeyboardButton(text="REJECT", callback_data=f"rej_{lid}")]])
    try:
        await context.bot.send_message(ADMIN_ID, f"Setoran {uid}:\n{update.message.text}", reply_markup=kb)
    except:
        pass
    return ConversationHandler.END

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id!= ADMIN_ID:
        return
    await q.answer()
    d = q.data
    if d.startswith("acc_"):
        _, uid, sid = d.split("_")
        c.execute("UPDATE users SET saldo=saldo+1000 WHERE id=?", (uid,))
        c.execute("UPDATE setoran SET status='APPROVED' WHERE id=?", (sid,))
        conn.commit()
        await q.edit_message_text(f"Approved {sid}")
        try:
            await context.bot.send_message(int(uid), "ACC +1000")
        except:
            pass
    else:
        sid = d.split("_")[1]
        c.execute("UPDATE setoran SET status='REJECTED' WHERE id=?", (sid,))
        conn.commit()
        await q.edit_message_text(f"Rejected {sid}")

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(entry_points=[CallbackQueryHandler(menu_handler, pattern="^(bebas|captcha)$")], states={ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, setor_handler)]}, fallbacks=[])
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(
