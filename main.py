import sqlite3, requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = '8914843920:AAElvXYtPOEKAKmVxrhNWdzSeQA4BS2dn5U'
ADMIN_ID = 6523631884
ASK = 1

conn = sqlite3.connect('jobgmail.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, saldo INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS setoran (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, data TEXT, status TEXT, waktu TEXT)')
conn.commit()

def sholat():    
try:    
r = requests.get('https://api.aladhan.com/v1/timingsByCity?city=Semarang&country=Indonesia&method=20', timeout=5).json()
t = r['data']['timings']
return '🕌 JADWAL SHOLAT SEMARANG\n🌙 Subuh '+t['Fajr']+' | ☀️ Dzuhur '+t['Dhuhr']+'\n🌤️ Ashar '+t['Asr']+' | 🌇 Maghrib '+t['Maghrib']+' | 🌃 Isya '+t['Isha']
except:
return '🕌 JADWAL SHOLAT SEMARANG\n🌙 Subuh 04:06 | ☀️ Dzuhur 11:31\n🌤️ Ashar 14:36 | 🌇 17:35 | 🌃 18:44'

def menu():
kb = [
[InlineKeyboardButton('📥 AMBIL TUGAS', callback_data='ambil')],
[InlineKeyboardButton('🔓 BEBAS RULES', callback_data='bebas'), InlineKeyboardButton('🤖 SETOR CAPTCHA', callback_data='captcha')],
[InlineKeyboardButton('⚙️ Generator', callback_data='gen'), InlineKeyboardButton('📜 Aturan & Info', callback_data='aturan')],
[InlineKeyboardButton('👥 Referral', callback_data='ref'), InlineKeyboardButton('💰 Dompet', callback_data='dompet')],
[InlineKeyboardButton('📊 Riwayat', callback_data='riwayat'), InlineKeyboardButton('🆘 Bantuan', callback_data='help')]
]
return InlineKeyboardMarkup(kb)

def back():
return InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Kembali ke Menu', callback_data='back')]])

async def start(update, context):
c.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (update.effective_user.id,))
conn.commit()
jam = datetime.now().strftime('%H:%M')
txt = sholat() + '\n━━━━━━━━━━━━━━\n⏰ WIB ' + jam + ' Semarang\n👋 Pilih Menu:'
await update.message.reply_text(txt, reply_markup=menu())

async def ask(update, context):
q = update.callback_query
await q.answer()
context.user_data['tipe'] = q.data
await q.message.reply_text('📩 Kirim data '+q.data.upper()+'\nFormat: email|password')
return ASK

async def menu_h(update, context):
q = update.callback_query
await q.answer()
d = q.data
uid = q.from_user.id
if d == 'back':
jam = datetime.now().strftime('%H:%M')
txt = sholat() + '\n━━━━━━━━━━━━━━\n⏰ WIB ' + jam + ' Semarang\n👋 Pilih Menu:'
await q.edit_message_text(txt, reply_markup=menu())
return
if d == 'aturan':
a1 = '📜 ATURAN & INFO\n\n'
a2 = '1️⃣ Wajib logout email\n'
a3 = '2️⃣ Jangan otak-atik akun\n'
a4 = '3️⃣ No verif & No tap\n'
a5 = '4️⃣ No ganti password\n'
a6 = '5️⃣ Curang = Banned\n'
a7 = '6️⃣ Wajib hapus keamanan\n'
a8 = '7️⃣ Pay 24-48 jam DANA'
await q.edit_message_text(a1+a2+a3+a4+a5+a6+a7+a8, reply_markup=back())
return
if d == 'dompet':
c.execute('SELECT saldo FROM users WHERE id=?', (uid,))
r = c.fetchone()
s = r[0] if r else 0
await q.edit_message_text('💰 Dompet: Rp '+str(s), reply_markup=back())
return
await q.edit_message_text('🚧 Fitur '+d+' segera', reply_markup=back())

async def setor(update, context):
uid = update.effective_user.id
txt = update.message.text.strip()
if '|' not in txt:
await update.message.reply_text('❌ Format salah! Pakai |')
return ASK
waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
c.execute('INSERT INTO setoran (user_id, data, status, waktu) VALUES (?,?,?,?)', (uid, txt, 'PENDING', waktu))
conn.commit()
lid = c.lastrowid
await update.message.reply_text('✅ Berhasil disetor!', reply_markup=menu())
kb = InlineKeyboardMarkup([[InlineKeyboardButton(text='✅ ACC', callback_data=f'acc_{uid}_{lid}'), InlineKeyboardButton(text='❌ REJECT', callback_data=f'rej_{lid}')]])
try:
await context.bot.send_message(ADMIN_ID, '🔥 SETORAN BARU dari '+str(uid)+'\n'+txt, reply_markup=kb)
except:
pass
return ConversationHandler.END

async def admin_cb(update, context):
q = update.callback_query
if q.from_user.id!= ADMIN_ID:
return
await q.answer()
d = q.data
if d.startswith('acc_'):
_, uid, sid = d.split('_')
c.execute('UPDATE users SET saldo=saldo+1000 WHERE id=?', (uid,))
c.execute('UPDATE setoran SET status="APPROVED" WHERE id=?', (sid,))
conn.commit()
await q.edit_message_text('✅ Approved '+sid)
try:
await context.bot.send_message(int(uid), '✅ ACC +1000')
except:
pass
else:
sid = d.split('_')[1]
c.execute('UPDATE setoran SET status="REJECTED" WHERE id=?', (sid,))
conn.commit()
await q.edit_message_text('❌ Rejected '+sid)

def main():
app = Application.builder().token(TOKEN).build()
conv = ConversationHandler(
entry_points=[CallbackQueryHandler(ask, pattern='^(bebas|captcha)$')],
states={ASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, setor)]},
fallbacks=[CommandHandler('start', start)],
per_message=False
)
app.add_handler(CommandHandler('start', start))
app.add_handler(conv)
app.add_handler(CallbackQueryHandler(menu_h, pattern='^(back|aturan|dompet|riwayat|ambil|gen|ref|help)$'))
app.add_handler(CallbackQueryHandler(admin_cb, pattern='^(acc_|rej_)'))
app.run_polling()

if __name__ == '__main__':
main()
