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
        [InlineKeyboardButton("⚡ AMBIL TUGAS", callback_data="ambil_tugas")],
        [InlineKeyboardButton("📩 BEBAS RULES", callback_data="bebas"), InlineKeyboardButton("🔐 SETOR CAPTCHA", callback_data="captcha")],
        [InlineKeyboardButton("📧 Generator", callback_data="generator"), InlineKeyboardButton("📜 Aturan & Info", callback_data="aturan")],
        [InlineKeyboardButton("👥 Referral", callback_data="referral"), InlineKeyboardButton("💰 Dompet (Tarik Saldo)", callback_data="dompet")],
        [InlineKeyboardButton("📊 Riwayat", callback_data="riwayat"), InlineKeyboardButton("🆘 Bantuan", callback_data="bantuan")],
        [InlineKeyboardButton("🤖 Bot Nokos", url="https://t.me/nokos_bot")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    aturan_text = (
        "📜 *ATURAN & INFO UMUM*\n\n"
        "1️⃣ Wajib logout email dari HP\n"
        "2️⃣ Jangan otak-atik akun jika sudah di setor\n"
        "3️⃣ No verif & No tap tap\n"
        "4️⃣ Dilarang mengganti password setelah di setor\n"
        "5️⃣ Ketauan curang = Banned/No payment\n"
        "6️⃣ Wajib hapus semua keamanan\n"
        "7️⃣ Review & pay estimasi 24-48 jam (senin - jumat)\n"
        "8️⃣ Hanya melayani payment via DANA\n\n"
        "❗ *LARANGAN:*\n"
        "• Email dot-trick (variasi titik) = DILARANG\n"
        "• Password SALAH = Banned"
    )
    text = f"{aturan_text}\n\nWIB\nPilih Menu:"
    await update.message.reply_text(text, reply_markup=get_menu(), parse_mode='Markdown')

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data == "ambil_tugas":
        await query.message.reply_text("TUGAS AKTIF:\n1. Buat Gmail baru (manual)\n2. Format: email|password|recovery\nKlik BEBAS RULES untuk setor", reply_markup=get_menu())
    elif data in ["bebas", "captcha"]:
        context.user_data["tipe"] = data
        await query.message.reply_text(f"Kirim data Gmail untuk {data.upper()} format:\nemail|password\nContoh: budi123@gmail.com|pass123", reply_markup=get_menu())
        return ASK_EMAIL
    elif data == "dompet":
        c.execute("SELECT saldo FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        saldo = row[0] if row else 0
        await query.message.reply_text(f"Dompet: Rp {saldo}\nUntuk Tarik Saldo hubungi Admin. DANA Manual.", reply_markup=get_menu())
    elif data == "riwayat":
        c.execute("SELECT data, status, waktu FROM setoran WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
        rows = c.fetchall()
        txt = "Belum ada riwayat." if not rows else "\n".join([f"[{r[2]}] - {r[0]} | {r[1]}" for r in rows])
        await query.message.reply_text(f"Riwayat:\n{txt}", reply_markup=get_menu())
    else:
        await query.message.reply_text(f"Fitur {data} segera hadir.", reply_markup=get_menu())
    return ConversationHandler.END

async def setor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data_text = update.message.text
    tipe = context.user_data.get("tipe", "bebas")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO setoran (user_id, data, status, waktu) VALUES (?,?,?,?)", (user_id, data_text, f"PENDING-{tipe}", waktu))
    conn.commit()
    await update.message.reply_text("✅ Berhasil disetor! Menunggu pengecekan manual Admin 1x24 jam.", reply_markup=get_menu())
    kb_admin = InlineKeyboardMarkup([[InlineKeyboardButton("✅ ACC +1000", callback_data=f"acc_{user_id}_{c.lastrowid}"), InlineKeyboardButton("❌ REJECT", callback_data=f"rej_{c.lastrowid}")]])
    try:
        await context.bot.send_message(ADMIN_ID, f"Setoran baru dari {user_id} [{tipe}]:\n{data_text}", reply_markup=kb_admin)
    except:
        pass
    return ConversationHandler.END

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    from_user_id = query.from_user.id
    if from_user_id!= ADMIN_ID:
        await query.answer("Bukan admin!")
        return
    await query.answer()
    data = query.data
    if data.startswith("acc_"):
        _, uid, sid = data.split("_")
        c.execute("UPDATE users SET saldo = saldo + 1000 WHERE id=?", (uid,))
        c.execute("UPDATE setoran SET status='APPROVED' WHERE id=?", (sid,))
        conn.commit()
        await query.edit_message_text(f"✅ Approved {sid} untuk {uid}")
        try:
            await context.bot.send_message(int(uid), "✅ Setoran kamu di ACC + Rp 1000!")
        except:
            pass
    elif data.startswith("rej_"):
        sid = data.split("_")[1]
        c.execute("UPDATE setoran SET status='REJECTED' WHERE id=?", (sid,))
        conn.commit()
        await query.edit_message_text(f"❌ Rejected {sid}")

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_handler, pattern="^(bebas|captcha)$")],
        states={ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, setor_handler)]},
        fallbacks=[]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(acc_|rej_)"))
    app.add_handler(conv)
    print("Bot JOBGMAIL jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
