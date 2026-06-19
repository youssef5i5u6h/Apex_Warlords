import os, json, telebot, threading
from flask import Flask
from telebot import types

app = Flask(__name__)

# --- SETTINGS ---
TOKEN = "8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM" 
OWNER_ID = 1609075265
# تأكد أن البوت "أدمن" في هذه القنوات
PAYMENT_CHANNEL = "@Apex_payment1" 
WITHDRAW_CHANNEL = "@lil_10l"
MAIN_CHANNEL = "@lS_3P"
MINI_APP_URL = "https://apexwarlords-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
user_states = {} 

def load_data():
    if not os.path.exists('data.json'): return {"users": {}, "admins": [OWNER_ID]}
    with open('data.json', 'r') as f: return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f: json.dump(data, f)

# --- KEYBOARDS ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⛏ Go to Mining", web_app=types.WebAppInfo(url=MINI_APP_URL)))
    markup.add(types.InlineKeyboardButton("💰 Deposit", callback_data="dep_req"),
               types.InlineKeyboardButton("💸 Withdraw", callback_data="with_req"))
    markup.add(types.InlineKeyboardButton("📢 Main Channel", url="https://t.me/lS_3P"))
    return markup

# --- BOT LOGIC ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    data = load_data()
    if uid not in data["users"]: 
        data["users"][uid] = {"name": m.from_user.first_name}
        save_data(data)
    bot.send_message(m.chat.id, f"Welcome {m.from_user.first_name}! Choose an option:", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    
    # طلبات المستخدم
    if call.data == "dep_req":
        user_states[uid] = "waiting_dep"
        bot.answer_callback_query(call.id, "Please send your payment screenshot.")
    
    elif call.data == "with_req":
        user_states[uid] = "waiting_with"
        bot.answer_callback_query(call.id, "Please enter the amount.")

    # قرارات الأدمن (Approve / Reject)
    elif call.data.startswith("app_dep_"):
        target_uid = call.data.split("_")[2]
        bot.send_message(target_uid, "✅ Your deposit has been approved!")
        bot.edit_message_text(call.message.text + "\n\nStatus: APPROVED", call.message.chat.id, call.message.message_id)
    
    elif call.data.startswith("rej_dep_"):
        target_uid = call.data.split("_")[2]
        bot.send_message(target_uid, "❌ Your deposit has been rejected.")
        bot.edit_message_text(call.message.text + "\n\nStatus: REJECTED", call.message.chat.id, call.message.message_id)

    elif call.data.startswith("app_with_"):
        target_uid = call.data.split("_")[2]
        bot.send_message(target_uid, "✅ Your withdrawal has been sent!")
        bot.edit_message_text(call.message.text + "\n\nStatus: SENT", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['photo', 'text'])
def handle_input(m):
    uid = m.from_user.id
    state = user_states.get(uid)
    
    if state == "waiting_dep" and m.photo:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"app_dep_{uid}"),
                   types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_dep_{uid}"))
        bot.send_photo(PAYMENT_CHANNEL, m.photo[-1].file_id, caption=f"New Deposit Request\nUser: {m.from_user.first_name} ({uid})", reply_markup=markup)
        bot.reply_to(m, "✅ Proof sent to admin!")
        user_states[uid] = None
        
    elif state == "waiting_with" and m.text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"app_with_{uid}"),
                   types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_with_{uid}"))
        bot.send_message(WITHDRAW_CHANNEL, f"New Withdraw Request\nUser: {m.from_user.first_name} ({uid})\nAmount: {m.text}", reply_markup=markup)
        bot.reply_to(m, "✅ Request sent to admin!")
        user_states[uid] = None

# Admin Commands
@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id != OWNER_ID: return
    bot.reply_to(m, f"📊 Total Users: {len(load_data()['users'])}")

@bot.message_handler(commands=['broadcast'])
def broadcast(m):
    if m.from_user.id != OWNER_ID: return
    try:
        msg = m.text.split(maxsplit=1)[1]
        for uid in load_data()["users"]:
            try: bot.send_message(uid, msg)
            except: pass
        bot.reply_to(m, "✅ Done.")
    except: bot.reply_to(m, "Use: /broadcast [msg]")

threading.Thread(target=lambda: bot.infinity_polling()).start()

@app.route('/')
def home(): return "Bot Active"

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)

