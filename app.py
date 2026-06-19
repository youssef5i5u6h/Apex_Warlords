import os, json, telebot, threading
from flask import Flask
from telebot import types

app = Flask(__name__)

# الإعدادات
TOKEN = "8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM" 
OWNER_ID = 1609075265
PAYMENT_CHANNEL = "@Apex_payment1" 
WITHDRAW_CHANNEL = "@lil_10l"
BOT_CHANNEL = "@lS_3P"

bot = telebot.TeleBot(TOKEN)
user_states = {}

# القاموس
LANGS = {
    "ar": {
        "welcome": "أهلاً بك! اختر لغتك:",
        "main_menu": "مرحباً بك في بوت التعدين، اختر ما تريد:",
        "btn_mining": "⛏ اذهب للتعدين",
        "btn_pay": "💳 قناة الدفع",
        "btn_with": "💸 قناة السحب",
        "btn_bot": "🤖 قناة البوت",
        "dep_msg": "أرسل صورة التحويل:",
        "with_msg": "اكتب المبلغ:",
        "done": "✅ تم التنفيذ."
    },
    "en": {
        "welcome": "Welcome! Choose language:",
        "main_menu": "Mining Bot Menu, choose option:",
        "btn_mining": "⛏ Go to Mining",
        "btn_pay": "💳 Payment Channel",
        "btn_with": "💸 Withdraw Channel",
        "btn_bot": "🤖 Bot Channel",
        "dep_msg": "Send transfer photo:",
        "with_msg": "Enter amount:",
        "done": "✅ Done."
    }
}

def load_data():
    if not os.path.exists('data.json'): return {"users": {}, "admins": [OWNER_ID]}
    with open('data.json', 'r') as f: return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f: json.dump(data, f)

def get_text(uid, key):
    data = load_data()
    lang = data.get("users", {}).get(str(uid), {}).get("lang", "ar")
    return LANGS[lang][key]

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    data = load_data()
    if uid not in data["users"]: 
        data["users"][uid] = {"lang": "ar"}
        save_data(data)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("العربية 🇸🇦", callback_data="lang:ar"),
               types.InlineKeyboardButton("English 🇺🇸", callback_data="lang:en"))
    bot.send_message(m.chat.id, "Welcome / أهلاً بك. اختر لغتك:", reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id != OWNER_ID: return
    data = load_data()
    bot.reply_to(m, f"📊 عدد المستخدمين: {len(data.get('users', {}))}")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.from_user.id != OWNER_ID: return
    try:
        msg = m.text.split(maxsplit=1)[1]
        for uid in load_data().get("users", {}):
            try: bot.send_message(uid, msg)
            except: pass
        bot.reply_to(m, "✅ تم الإرسال للكل.")
    except: bot.reply_to(m, "استخدم: /broadcast [الرسالة]")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = str(call.from_user.id)
    if call.data.startswith("lang:"):
        lang = call.data.split(":")[1]
        data = load_data()
        data["users"][uid] = {"lang": lang}
        save_data(data)
        # القائمة الرئيسية
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(get_text(uid, "btn_mining"), callback_data="mining_act"))
        markup.add(types.InlineKeyboardButton(get_text(uid, "btn_pay"), url="https://t.me/Apex_payment1"))
        markup.add(types.InlineKeyboardButton(get_text(uid, "btn_with"), url="https://t.me/lil_10l"))
        markup.add(types.InlineKeyboardButton(get_text(uid, "btn_bot"), url="https://t.me/lS_3P"))
        bot.edit_message_text(get_text(uid, "main_menu"), call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "mining_act":
        bot.answer_callback_query(call.id, "جاري فتح التعدين...")
        # هنا تقدر تحط زرار يودي لرابط التعدين بتاعك
        bot.send_message(call.message.chat.id, "جاري بدء التعدين... (ضع الرابط هنا)")

@bot.message_handler(content_types=['photo', 'text'])
def handle_input(m):
    if m.text and m.text.startswith('/'): return
    uid = m.from_user.id
    # هنا تحط منطق استلام صور الإيداع أو رسائل السحب لو عايز تضيفهم تاني
    bot.reply_to(m, "استخدم الأزرار الموجودة في القائمة.")

threading.Thread(target=lambda: bot.infinity_polling()).start()
@app.route('/')
def home(): return "Bot Active"
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)

