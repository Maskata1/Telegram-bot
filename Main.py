import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time

TOKEN = "8796481252:AAEGUgIA3LSIot0squzDD-RKnc9W6shoa20"
GROUP_ID = -1003987883686

# 🔒 SADECE BU ID'LER ONAY/RED YAPABİLİR
ADMINS = [8273423886]

KANAL_LINK = "https://t.me/kanal_linkin"
GRUP_LINK = "https://t.me/grup_linkin"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

users = {}
applications = {}

red_mode = {
    "active": False,
    "target": None
}

# 🌐 KEEP ALIVE
app = Flask('')

@app.route('/')
def home():
    return "NXQL BOT AKTİF"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# ⚔️ START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚔️ BAŞVURU YAP", callback_data="basla"))

    bot.send_message(
        message.chat.id,
        "<b>⚔️ NXQL GANG</b>\n\n"
        "🛡️ <b>Seçkin oyuncuların bulunduğu özel ekip.</b>\n\n"
        "📌 Disiplin, sadakat ve güç bizim temelimizdir.\n\n"
        "🎯 <b>Hazırsan başvurunu başlat.</b>",
        reply_markup=markup
    )

# 🔘 BAŞLA
@bot.callback_query_handler(func=lambda call: call.data == "basla")
def basla(call):
    users[call.message.chat.id] = {"step": 1}
    bot.send_message(call.message.chat.id, "📌 Telegram kullanıcı adını yaz:")

# 🧠 MESAJ AKIŞI
@bot.message_handler(content_types=['text'])
def handle(message):
    uid = message.chat.id
    text = message.text

    # 🔴 RED MOD
    if red_mode["active"] and uid == GROUP_ID:
        target = red_mode["target"]
        user = applications.get(target)

        if user:
            bot.send_message(
                target,
                f"❌ <b>Başvurun reddedildi</b>\n\n📌 Sebep:\n{text}"
            )

            bot.send_message(
                GROUP_ID,
                f"🔴 RED VERİLDİ\n👤 {user['oyuncu']}\n📌 {text}"
            )

            applications.pop(target)

        red_mode["active"] = False
        red_mode["target"] = None
        return

    if uid not in users:
        return

    step = users[uid]["step"]

    if step == 1:
        users[uid]["telegram"] = text
        users[uid]["step"] = 2
        bot.send_message(uid, "🎮 Oyuncu adını yaz:")

    elif step == 2:
        users[uid]["oyuncu"] = text
        users[uid]["step"] = 3
        bot.send_message(uid, "🆔 Oyuncu ID yaz:")

    elif step == 3:
        users[uid]["id"] = text

        applications[uid] = users[uid]

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ ONAYLA", callback_data=f"onay_{uid}"),
            types.InlineKeyboardButton("❌ REDDET", callback_data=f"red_{uid}")
        )

        bot.send_message(
            GROUP_ID,
            f"⚔️ <b>NXQL BAŞVURU</b>\n\n"
            f"👤 {users[uid]['telegram']}\n"
            f"🎮 {users[uid]['oyuncu']}\n"
            f"🆔 {users[uid]['id']}",
            reply_markup=markup
        )

        bot.send_message(uid, "✅ Başvurun alındı. İnceleme bekleniyor.")
        users.pop(uid)

# 🟢 ONAY
@bot.callback_query_handler(func=lambda call: call.data.startswith("onay_"))
def approve(call):
    if call.from_user.id not in ADMINS:
        return

    uid = int(call.data.split("_")[1])
    user = applications.get(uid)

    if not user:
        return

    bot.send_message(
        uid,
        "🟢 <b>NXQL KARARI</b>\n\n"
        "Başvurun onaylandı. Aramıza hoş geldin ⚔️\n\n"
        "📢 Kanal:\n"
        f"{KANAL_LINK}\n\n"
        "💬 Sohbet:\n"
        f"{GRUP_LINK}"
    )

    bot.edit_message_text("🟢 ONAYLANDI", GROUP_ID, call.message.message_id)
    applications.pop(uid)

# 🔴 RED
@bot.callback_query_handler(func=lambda call: call.data.startswith("red_"))
def reject(call):
    if call.from_user.id not in ADMINS:
        return

    uid = int(call.data.split("_")[1])

    red_mode["active"] = True
    red_mode["target"] = uid

    bot.send_message(
        GROUP_ID,
        "❌ RED MOD AKTİF\n\n📌 Lütfen reddetme sebebini buraya yazınız."
    )

# 🚀 BAŞLAT
keep_alive()
print("⚔️ NXQL BOT AKTİF")
bot.polling(none_stop=True)
