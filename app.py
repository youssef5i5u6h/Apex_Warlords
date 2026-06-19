import os, json, telebot, threading, time
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- الإعدادات ---
TOKEN = "8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM"
OWNER_ID = 1609075265
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'data.json'

# --- العناوين ---
WALLETS = {
    "USDT_BEP20": "0x0aae3b8ed565178c5224296429310959536a80b6",
    "USDT_TRC20": "TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni",
    "TON": "UQAO-l2K9qQtbHzLGiWyyGRtsaGBh0t82qHaa2GDMqq49Lp8"
}

# --- إدارة البيانات ---
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f: json.dump({"users": {}}, f)
        return {"users": {}}
    with open(DATA_FILE, 'r') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f)

# --- كود الواجهة (Frontend) بتصميم Dark Gaming ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Warlords</title>
    <style>
        body { background: #0e0e15; color: #fff; font-family: sans-serif; margin: 0; padding-bottom: 80px; }
        .header { padding: 20px; background: #1a1a2e; text-align: center; border-bottom: 2px solid #303050; }
        .card { background: #1a1a2e; margin: 15px; padding: 15px; border-radius: 15px; border: 1px solid #4a4a80; }
        .btn { background: linear-gradient(90deg, #6a11cb, #2575fc); border: none; padding: 12px; border-radius: 8px; color: white; width: 100%; font-weight: bold; margin-top: 10px; }
        .nav-bar { position: fixed; bottom: 0; width: 100%; background: #1a1a2e; display: flex; justify-content: space-around; padding: 15px 0; border-top: 2px solid #303050; }
        .tab { color: #aaa; text-decoration: none; font-size: 14px; text-align: center; }
        .tab.active { color: #fff; border-bottom: 2px solid #2575fc; }
        select { width: 100%; padding: 10px; background: #111; color: #fff; border-radius: 5px; border: 1px solid #444; }
    </style>
</head>
<body>
    <div class="header">
        <h2>💰 Balance: {{user.balance}} $</h2>
        <p>Mining Power: {{user.miners * 10}} H/S</p>
    </div>

    <div class="card">
        <h3>Deposit Funds</h3>
        <select id="cur" onchange="updateAddr()">
            <option value="USDT_BEP20">USDT BEP20</option>
            <option value="USDT_TRC20">USDT TRC20</option>
            <option value="TON">TON</option>
        </select>
        <p id="addr" style="word-break: break-all; margin: 10px 0; color: #00d4ff;">{{wallets['USDT_BEP20']}}</p>
        <form action="/deposit" method="post" enctype="multipart/form-data">
            <input type="hidden" name="id" value="{{user_id}}">
            <input type="hidden" name="currency" id="hidden_cur" value="USDT_BEP20">
            <input type="file" name="file" required style="width:100%; margin-bottom:10px;">
            <button class="btn" type="submit">Submit Deposit Proof</button>
        </form>
    </div>

    <div class="nav-bar">
        <a class="tab active">⛏ Miners</a>
        <a class="tab">📋 Tasks</a>
        <a class="tab">💳 Wallet</a>
    </div>

    <script>
        const wallets = {{wallets|tojson}};
        function updateAddr(){
            let c = document.getElementById('cur').value;
            document.getElementById('addr').innerText = wallets[c];
            document.getElementById('hidden_cur').value = c;
        }
    </script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def index():
    uid = request.args.get('id')
    data = load_data()
    if uid not in data['users']:
        data['users'][uid] = {"balance": 0, "miners": 0}
        save_data(data)
    return render_template_string(HTML_TEMPLATE, user=data['users'][uid], user_id=uid, wallets=WALLETS)

@app.route('/deposit', methods=['POST'])
def deposit():
    uid = request.form['id']
    currency = request.form['currency']
    file = request.files['file']
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{uid}"),
        telebot.types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{uid}")
    )
    bot.send_photo(OWNER_ID, file, caption=f"Deposit Request\nUser ID: {uid}\nCurrency: {currency}", reply_markup=markup)
    return "<h3>Success! Proof sent to Admin.</h3>"

# --- البوت ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    url = f"https://apexwarlords-production.up.railway.app?id={uid}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Launch App 🚀", web_app=telebot.types.WebAppInfo(url=url)))
    bot.send_message(m.chat.id, "Welcome to Apex Warlords!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user.id != OWNER_ID: return
    uid = call.data.split("_")[1]
    if call.data.startswith("app_"):
        bot.send_message(uid, "✅ Your deposit was approved!")
        bot.edit_message_caption(call.message.caption + "\n\nStatus: APPROVED", call.message.chat.id, call.message.message_id)

# --- تشغيل ---
threading.Thread(target=lambda: bot.infinity_polling()).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
