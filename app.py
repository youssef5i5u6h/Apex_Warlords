import os, json, telebot, threading
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
TOKEN = "8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM"
OWNER_ID = 1609075265
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'data.json'

# --- تحميل البيانات ---
def load_data():
    if not os.path.exists(DATA_FILE): return {"users": {}}
    with open(DATA_FILE, 'r') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f)

# --- الواجهة (HTML/CSS/JS) ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #0e0e15; color: white; font-family: sans-serif; margin: 0; padding-bottom: 80px; }
        .header { padding: 20px; background: #1a1a2e; border-bottom: 2px solid #303050; display: flex; justify-content: space-between; }
        .tab-content { display: none; padding: 15px; }
        .tab-content.active { display: block; }
        .card { background: #1a1a2e; padding: 15px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #4a4a80; }
        .btn-buy { background: #eab308; color: black; font-weight: bold; padding: 10px; border-radius: 8px; border: none; width: 100%; }
        .nav-bar { position: fixed; bottom: 0; width: 100%; background: #1a1a2e; display: flex; justify-content: space-around; padding: 15px 0; border-top: 2px solid #303050; }
        .nav-btn { color: #aaa; cursor: pointer; text-align: center; }
        .nav-btn.active { color: #fff; }
    </style>
</head>
<body>
    <div class="header">
        <div>💰 Balance: <span id="bal">{{user.balance}}</span> $</div>
        <div>Mining Power: {{user.miners * 10}} H/S</div>
    </div>

    <div id="miners" class="tab-content active">
        <div class="card">
            <h3>PEPE Engine</h3>
            <p>H/S: 289.3519</p>
            <button class="btn-buy" onclick="buy('pepe')">Buy (1000$)</button>
        </div>
        <div class="card">
            <h3>SHIB CORE</h3>
            <p>H/S: 18.5185</p>
            <button class="btn-buy" onclick="buy('shib')">Buy (100$)</button>
        </div>
    </div>

    <div id="tasks" class="tab-content">
        <h3>Daily Tasks</h3>
        <div class="card">Launch @DoodlePlayBot - Reward: 0.1$</div>
    </div>

    <div id="wallet" class="tab-content">
        <div class="card">
            <h3>Deposit</h3>
            <p>Address: <code>TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni</code></p>
            <input type="file" style="width:100%">
            <button class="btn-buy" style="background:#2563eb; color:white; margin-top:10px;">Submit Proof</button>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-btn active" onclick="show('miners', this)">⛏ Miners</div>
        <div class="nav-btn" onclick="show('tasks', this)">📋 Tasks</div>
        <div class="nav-btn" onclick="show('wallet', this)">💳 Wallet</div>
    </div>

    <script>
        function show(id, el) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(t => t.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }
        function buy(item) { fetch('/buy?item='+item+'&id={{user_id}}').then(r=>location.reload()) }
    </script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def index():
    uid = request.args.get('id', '123')
    data = load_data()
    if uid not in data['users']: data['users'][uid] = {"balance": 100, "miners": 0}
    return render_template_string(HTML, user=data['users'][uid], user_id=uid)

@app.route('/buy')
def buy():
    uid = request.args.get('id')
    item = request.args.get('item')
    data = load_data()
    if data['users'][uid]['balance'] >= 100:
        data['users'][uid]['balance'] -= 100
        data['users'][uid]['miners'] += 1
        save_data(data)
    return "OK"

# --- تشغيل البوت ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.InlineKeyboardMarkup()
    url = f"https://apexwarlords-production.up.railway.app?id={m.from_user.id}"
    markup.add(telebot.types.InlineKeyboardButton("Launch App 🚀", web_app=telebot.types.WebAppInfo(url=url)))
    bot.send_message(m.chat.id, "Welcome to Apex Warlords!", reply_markup=markup)

threading.Thread(target=lambda: bot.infinity_polling()).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)

