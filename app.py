import os
import json
import time
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot

app = Flask(__name__)

# --- 🔒 Threading Lock ---
data_lock = threading.Lock()

# --- ⚙️ Core Configuration ---
TOKEN = "8895527275:AAGg5nDAdS2O2NKDX8IAjcPt7Dknz9CgpL4"
OWNER_ID = 1609075265  # الآيدي الخاص بك
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'data.json'

PAYMENT_CHANNEL_ID = "@Apex_payment1"     
WITHDRAWAL_CHANNEL_ID = "@lil_10l"       
NEWS_CHANNEL_LINK = "https://t.me/lS_3P"   

WALLETS = {
    "USDT_BEP20": "0x0aae3b8ed565178c5224296429310959536a80b6",
    "USDT_TRC20": "TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni",
    "TON": "UQAO-l2K9qQtbHzLGiWyyGRtsaGBh0t82qHaa2GDMqq49Lp8"
}

MINER_TYPES = {
    "doge": {"name": "DOGE Miner", "cost": 0.5, "speed": 0.0120, "tier": "STARTER", "color": "#cbd5e1"},
    "wif": {"name": "WIF Turbine", "cost": 2.5, "speed": 0.0463, "tier": "COMMON", "color": "#22c55e"},
    "pengu": {"name": "PENGU COLD", "cost": 5.0, "speed": 0.2894, "tier": "COMMON", "color": "#22c55e"},
    "neiro": {"name": "NEIRO FOMO", "cost": 10.0, "speed": 1.3310, "tier": "RARE", "color": "#3b82f6"},
    "popcat": {"name": "POPCAT PUMP", "cost": 25.0, "speed": 3.6169, "tier": "RARE", "color": "#3b82f6"},
    "asteroid": {"name": "ASTEROID NODE", "cost": 50.0, "speed": 8.1019, "tier": "EPIC", "color": "#a855f7"},
    "shib": {"name": "SHIB CORE", "cost": 100.0, "speed": 18.5185, "tier": "EPIC", "color": "#a855f7"},
    "floki": {"name": "FLOKI RIG", "cost": 250.0, "speed": 57.7040, "tier": "EPIC", "color": "#a855f7"},
    "pepe": {"name": "PEPE Engine", "cost": 1000.0, "speed": 289.3519, "tier": "ELITE", "color": "#f97316"},
    "mtonga": {"name": "MTONGA Reactor", "cost": 5000.0, "speed": 777.0000, "tier": "LEGENDARY", "color": "#ef4444"}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f: json.dump({"users": {}}, f)
        return {"users": {}}
    with open(DATA_FILE, 'r') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

def update_mining(user):
    now = time.time()
    last = user.get("last_calc", now)
    total_speed = 0.0100 
    if "miners" in user and isinstance(user["miners"], dict):
        for m_id, count in user["miners"].items():
            if m_id in MINER_TYPES:
                total_speed += MINER_TYPES[m_id]["speed"] * count
    elapsed = now - last
    user["mined"] = user.get("mined", 0.0) + (total_speed * (elapsed / 3600.0))
    user["last_calc"] = now
    return total_speed

# --- Premium Web UI Dashboard ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Apex Mining Premium</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #05070f; color: #f8fafc; margin: 0; padding-bottom: 110px; overflow-x: hidden; background-image: radial-gradient(circle at 50% 0%, #111827 0%, #05070f 70%); }
        .top-bar { display: flex; flex-direction: column; align-items: center; padding: 18px 15px; background: rgba(10, 15, 30, 0.7); border-bottom: 1px solid rgba(255, 255, 255, 0.06); backdrop-filter: blur(20px); position: sticky; top: 0; z-index: 1000; }
        .logo-area { font-size: 26px; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px; text-shadow: 0 0 20px rgba(0, 242, 254, 0.3); margin-bottom: 15px; }
        .stats-row { display: flex; width: 100%; justify-content: space-between; gap: 14px; }
        .stat-box { flex: 1; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 16px; font-weight: 800; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: 0.3s; }
        .stat-box.cash { color: #10b981; border-color: rgba(16, 185, 129, 0.25); background: linear-gradient(180deg, rgba(16,185,129,0.05) 0%, rgba(0,0,0,0) 100%); }
        .stat-box.gems { color: #00f2fe; border-color: rgba(0, 242, 254, 0.25); background: linear-gradient(180deg, rgba(0,242,254,0.05) 0%, rgba(0,0,0,0) 100%); }
        .page { display: none; padding: 20px 15px; animation: slideUp 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
        .page.active { display: block; }
        .miner-card { background: linear-gradient(145deg, rgba(20, 28, 47, 0.9) 0%, rgba(11, 16, 28, 0.9) 100%); border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); padding: 18px; margin-bottom: 16px; position: relative; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.4); overflow: hidden; transition: 0.2s; }
        .miner-name { font-size: 19px; font-weight: 800; color: #fff; }
        .btn-buy { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #05070f; border: none; font-weight: 900; padding: 14px 24px; border-radius: 16px; cursor: pointer; box-shadow: 0 6px 20px rgba(217, 119, 6, 0.3); font-size: 14px; }
        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .reactor-core { width: 200px; height: 200px; position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; }
        .reactor-sphere { width: 130px; height: 130px; background: radial-gradient(circle, #00f2fe 0%, #1d4ed8 100%); border-radius: 50%; box-shadow: 0 0 50px rgba(0, 242, 254, 0.6); animation: pulse 2s infinite alternate; }
        .reactor-outer-ring { position: absolute; width: 170px; height: 170px; border: 2px dashed rgba(0, 242, 254, 0.3); border-radius: 50%; animation: rotateRing 8s linear infinite; }
        @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.08); } }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .claim-panel { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); width: 100%; padding: 22px; border-radius: 24px; text-align: center; box-shadow: 0 8px 30px rgba(29, 78, 216, 0.4); cursor: pointer; margin-bottom: 25px; }
        .grid-menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 100%; }
        .grid-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 18px; text-align: center; cursor: pointer; font-weight: 700; transition: 0.2s; }
        .nav-bar { position: fixed; bottom: 20px; left: 4%; width: 92%; background: rgba(15, 22, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 10px 0; border-radius: 24px; backdrop-filter: blur(20px); z-index: 999; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #64748b; cursor: pointer; }
        .nav-item.active { color: #00f2fe; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="logo-area">APEX MINING</div>
        <div class="stats-row">
            <div class="stat-box cash">💵 <span id="display-cash">{{user.balance}}</span> $</div>
            <div class="stat-box gems">💎 <span>{{user.gems}}</span></div>
        </div>
    </div>

    <div id="page-main" class="page active">
        <div class="main-container">
            <div class="reactor-core">
                <div class="reactor-outer-ring"></div>
                <div class="reactor-sphere"></div>
            </div>
            <div class="claim-panel" onclick="claimMined()">
                <div style="font-size: 32px; font-weight: 900; color: #fff;"><span id="display-mined">0.000000</span></div>
                <div style="font-size: 14px; color: #93c5fd; margin-top: 6px;">اضغط لتجميع الأرباح المتولدة 🚀</div>
            </div>
            <div class="grid-menu">
                {% if user_id == '1609075265' %}
                <div class="grid-item" onclick="dailyReward()">🎁 مكافأة يومية</div>
                {% endif %}
                <div class="grid-item" onclick="window.open('{{news_link}}')">📢 قناة الأخبار</div>
            </div>
        </div>
    </div>

    <script>
        // دالة المكافأة اليومية
        function dailyReward() {
            fetch(`/api/daily_reward?id={{user_id}}`)
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }
        // [باقي دوال الجافاسكريبت هنا]
    </script>
</body>
</html>
"""

# --- Routes Logic ---
@app.route('/')
def index():
    uid = request.args.get('id', '1609075265')
    with data_lock:
        data = load_data()
        if uid not in data['users']:
            data['users'][uid] = {"balance": 0.0, "gems": 0, "mined": 0.0, "last_calc": time.time(), "miners": {}, "last_reward": 0.0}
        user = data['users'][uid]
        speed = update_mining(user)
        save_data(data)
    return render_template_string(HTML_TEMPLATE, user=user, user_id=uid, wallets=WALLETS, miner_types=MINER_TYPES, speed=round(speed, 4), news_link=NEWS_CHANNEL_LINK)

@app.route('/api/daily_reward')
def api_daily_reward():
    uid = request.args.get('id')
    # 🔒 أمان إضافي في الباكيند
    if int(uid) != OWNER_ID:
        return jsonify({"status": "error", "message": "غير مسموح لك بالوصول لهذه الميزة!"})
        
    now = time.time()
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        last_reward = user.get("last_reward", 0.0)
        if now - last_reward >= 86400:
            user["balance"] = round(user.get("balance", 0.0) + 0.10, 4)
            user["last_reward"] = now
            save_data(data)
            return jsonify({"status": "success", "message": "تم استلام المكافأة!"})
        else:
            return jsonify({"status": "error", "message": "لقد أخذت المكافأة اليوم! عد غداً."})

# [باقي المسارات المعتادة موجودة في الكود السابق]

@bot.message_handler(commands=['broadcast'])
def broadcast_to_all(message):
    # 📢 أمر الإذاعة محمي برمجياً
    if message.from_user.id != OWNER_ID:
        return
    # [كود الإذاعة...]
    pass

# ابدأ البوت
threading.Thread(target=lambda: bot.infinity_polling()).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

