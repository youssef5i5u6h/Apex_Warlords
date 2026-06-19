import os
import json
import time
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot

app = Flask(__name__)

# --- ⚙️ الإعدادات الأساسية وقنوات التليجرام الخاصة بك ---
TOKEN = "8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM"
OWNER_ID = 1609075265
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'data.json'

# 📢 تم ربط قنواتك الرسمية هنا بنجاح
PAYMENT_CHANNEL_ID = "@Apex_payment1"     # قناة إشعارات الإيداع
WITHDRAWAL_CHANNEL_ID = "@lil_10l"       # قناة إشعارات السحب
NEWS_CHANNEL_LINK = "https://t.me/lS_3P"   # قناة أخبار البوت الكبيرة

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

# --- إدارة قاعدة البيانات وجدولة الأرباح تلقائياً ---
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
    total_speed = 0.0
    
    if "miners" in user and isinstance(user["miners"], dict):
        for m_id, count in user["miners"].items():
            if m_id in MINER_TYPES:
                total_speed += MINER_TYPES[m_id]["speed"] * count
    
    elapsed = now - last
    user["mined"] = user.get("mined", 0.0) + (total_speed * (elapsed / 3600.0))
    user["last_calc"] = now
    return total_speed

# --- تصميم الواجهة الاحترافية (HTML/CSS/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Apex Warlords</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: linear-gradient(180deg, #09070f 0%, #120e24 100%); color: #ffffff; margin: 0; padding-bottom: 90px; overflow-x: hidden; }
        
        .top-bar { display: flex; flex-direction: column; align-items: center; padding: 15px; background: rgba(26, 21, 46, 0.7); border-bottom: 2px solid #2e2454; backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 1000; }
        .logo-area { font-size: 22px; font-weight: 900; color: #00d4ff; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); letter-spacing: 1px; margin-bottom: 10px; }
        .stats-row { display: flex; width: 100%; justify-content: space-between; gap: 10px; }
        .stat-box { flex: 1; background: #161233; border: 1px solid #3d306d; border-radius: 12px; padding: 10px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 14px; font-weight: bold; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }
        .stat-box.cash { color: #22c55e; }
        .stat-box.gems { color: #00d4ff; }

        .page { display: none; padding: 15px; animation: fadeIn 0.3s ease-in-out; }
        .page.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .miner-card { background: linear-gradient(135deg, #19143a 0%, #110d28 100%); border-radius: 20px; border: 1px solid #362b6b; padding: 15px; margin-bottom: 15px; position: relative; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 8px 20px rgba(0,0,0,0.4); }
        .miner-info { display: flex; flex-direction: column; gap: 4px; }
        .miner-name { font-size: 18px; font-weight: bold; color: #fff; }
        .miner-tier { position: absolute; top: 10px; left: 15px; font-size: 10px; font-weight: 900; padding: 3px 8px; border-radius: 20px; text-transform: uppercase; border: 1px solid currentColor; }
        .miner-speed { font-size: 13px; color: #a5b4fc; background: #1e1947; padding: 4px 8px; border-radius: 6px; display: inline-block; width: fit-content; margin-top: 5px; }
        .miner-owned { font-size: 12px; color: #fbbf24; margin-top: 2px; }
        .btn-buy { background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%); color: #000; border: none; font-weight: 900; padding: 10px 20px; border-radius: 12px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4); font-size: 14px; }
        .btn-buy:active { transform: scale(0.95); }

        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px 0; }
        .reactor-core { width: 180px; height: 180px; background: radial-gradient(circle, rgba(0,212,255,0.2) 0%, rgba(0,0,0,0) 70%); position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
        .reactor-sphere { width: 110px; height: 110px; background: linear-gradient(135deg, #00d4ff 0%, #0052d4 100%); border-radius: 50%; box-shadow: 0 0 30px #00d4ff, inset 0 0 15px #fff; animation: pulse 2s infinite alternate; }
        @keyframes pulse { from { transform: scale(1); box-shadow: 0 0 25px #00d4ff; } to { transform: scale(1.08); box-shadow: 0 0 45px #00d4ff; } }
        
        .claim-panel { background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); width: 100%; padding: 15px; border-radius: 18px; text-align: center; box-shadow: 0 5px 20px rgba(180, 83, 9, 0.5); cursor: pointer; margin-bottom: 20px; }
        .claim-amount { font-size: 24px; font-weight: 900; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .claim-label { font-size: 12px; color: #fef3c7; font-weight: bold; }

        .grid-menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; width: 100%; }
        .grid-item { background: #161233; border: 1px solid #362b6b; padding: 15px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; font-size: 14px; }

        .input-select { width: 100%; padding: 12px; background: #161233; border: 1px solid #362b6b; color: #fff; border-radius: 10px; font-weight: bold; margin-bottom: 15px; }
        .address-box { background: #090710; border: 1px dashed #4f46e5; padding: 12px; border-radius: 10px; font-size: 13px; word-break: break-all; text-align: center; color: #00d4ff; margin-bottom: 15px; font-family: monospace; }
        .btn-action { background: linear-gradient(90deg, #4f46e5, #2563eb); color: white; border: none; padding: 14px; width: 100%; font-weight: bold; border-radius: 12px; cursor: pointer; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }
        
        .task-card { background: #161233; border: 1px solid #2e2454; padding: 15px; border-radius: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; width: 100%; text-align: right; }
        .task-btn { background: #2563eb; border: none; color: white; padding: 8px 18px; border-radius: 8px; font-weight: bold; font-size: 12px; cursor: pointer; }

        .nav-bar { position: fixed; bottom: 0; left: 0; width: 100%; background: #120e25; border-top: 2px solid #2e2454; display: flex; justify-content: space-around; padding: 12px 0; box-shadow: 0 -5px 25px rgba(0,0,0,0.6); z-index: 999; }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; color: #7c72a1; cursor: pointer; flex: 1; font-size: 11px; font-weight: bold; transition: 0.2s; }
        .nav-item.active { color: #00d4ff; }
        .nav-icon { font-size: 20px; }
    </style>
</head>
<body>

    <div class="top-bar">
        <div class="logo-area">APEX WARLORDS</div>
        <div class="stats-row">
            <div class="stat-box cash">💵 <span id="display-cash">{{user.balance}}</span> $</div>
            <div class="stat-box gems">💎 <span>{{user.gems}}</span></div>
        </div>
    </div>

    <!-- 1. الرئيسية -->
    <div id="page-main" class="page active">
        <div class="main-container">
            <div class="reactor-core">
                <div class="reactor-sphere"></div>
            </div>
            <div class="claim-panel" onclick="claimMined()">
                <div class="claim-amount"><span id="display-mined">0.000000</span></div>
                <div class="claim-label">اضغط لتجميع الأرباح المتولدة الحالية 🚀</div>
            </div>
            <div class="grid-menu">
                <div class="grid-item" onclick="dailyReward()">🎁 مكافأة يومية</div>
                <div class="grid-item" onclick="alert('سيتم إتاحتها قريباً!')">⚡ تعزيز السرعة 4x</div>
                <div class="grid-item" onclick="alert('سيتم إتاحتها قريباً!')">🛡️ معارك التحالف</div>
                <div class="grid-item" onclick="window.open('{{news_link}}')">📢 قناة الأخبار</div>
            </div>
        </div>
    </div>

    <!-- 2. المعدنون -->
    <div id="page-miners" class="page">
        <p style="text-align: center; color: #a5b4fc; font-size: 13px;">سرعة التعدين الكلية الحالية: <span id="display-speed">{{speed}}</span> H/S</p>
        {% for m_id, m in miner_types.items() %}
        <div class="miner-card">
            <div class="miner-info">
                <span class="miner-tier" style="color: {{m.color}};">{{m.tier}}</span>
                <span class="miner-name">{{m.name}}</span>
                <span class="miner-speed">⚡ {{m.speed}} H/S</span>
                <span class="miner-owned">الكمية المملوكة: {{user.miners[m_id] or 0}}</span>
            </div>
            <button class="btn-buy" onclick="buyMiner('{{m_id}}')">شراء<br>{{m.cost}}$</button>
        </div>
        {% endfor %}
    </div>

    <!-- 3. المهام -->
    <div id="page-tasks" class="page">
        <div class="task-card">
            <div>
                <div style="font-weight:bold;">قم بتشغيل بوت @DoodlePlayBot</div>
                <div style="font-size:12px; color:#818cf8;">المكافأة: +0.01$ | +1💎</div>
            </div>
            <button class="task-btn" onclick="window.open('https://t.me/DoodlePlayBot')">فتح</button>
        </div>
        <div class="task-card">
            <div>
                <div style="font-weight:bold;">انضم لقناة التحديثات الرسمية للمشروع</div>
                <div style="font-size:12px; color:#818cf8;">المكافأة: +0.02$ | +2💎</div>
            </div>
            <button class="task-btn" onclick="window.open('{{news_link}}')">انضمام</button>
        </div>
    </div>

    <!-- 4. الأصدقاء -->
    <div id="page-friends" class="page" style="text-align:center; padding-top:20px;">
        <h3>دعوة الأصدقاء 👥</h3>
        <p style="color:#a5b4fc; font-size:14px;">قم بنسخ رابط الإحالة الخاص بك وتحصّل على 10% من أرباح أصدقائك!</p>
        <div class="address-box">https://t.me/YourBotName_Bot?start={{user_id}}</div>
        <button class="btn-action" onclick="navigator.clipboard.writeText('https://t.me/YourBotName_Bot?start={{user_id}}'); alert('تم نسخ رابط الإحالة الخاص بك بنجاح!');">نسخ الرابط</button>
    </div>

    <!-- 5. المحفظة -->
    <div id="page-wallet" class="page">
        <div style="background:#161233; padding:15px; border-radius:15px; border:1px solid #362b6b;">
            <h3 style="margin-top:0; text-align:center;">إيداع الأموال وشحن الحساب</h3>
            <label>اختر العملة الرقمية المراد الإيداع بها:</label>
            <select class="input-select" id="wallet-selector" onchange="changeWallet()">
                <option value="USDT_BEP20">USDT (BEP20)</option>
                <option value="USDT_TRC20">USDT (TRC20)</option>
                <option value="TON">TON Coin</option>
            </select>
            <label>عنوان المحفظة الخاص بنا للإرسال:</label>
            <div class="address-box" id="wallet-address">{{wallets['USDT_BEP20']}}</div>
            
            <form action="/deposit" method="post" enctype="multipart/form-data" style="margin-top:15px;">
                <input type="hidden" name="user_id" value="{{user_id}}">
                <input type="hidden" name="currency" id="hidden-currency" value="USDT_BEP20">
                <label>ارفع لقطة شاشة لإثبات التحويل (Screenshot):</label>
                <input type="file" name="file" required style="width:100%; margin:10px 0; color:#fff;">
                <button type="submit" class="btn-action">تأكيد وإرسال الإثبات للأدمن</button>
            </form>
        </div>
    </div>

    <!-- شريط التنقل السفلي -->
    <div class="nav-bar">
        <div class="nav-item active" onclick="switchPage('main', this)"><span class="nav-icon">🏠</span>الرئيسية</div>
        <div class="nav-item" onclick="switchPage('miners', this)"><span class="nav-icon">⛏️</span>المعدنون</div>
        <div class="nav-item" onclick="switchPage('tasks', this)"><span class="nav-icon">📋</span>المهام</div>
        <div class="nav-item" onclick="switchPage('friends', this)"><span class="nav-icon">👥</span>الأصدقاء</div>
        <div class="nav-item" onclick="switchPage('wallet', this)"><span class="nav-icon">💳</span>المحفظة</div>
    </div>

    <script>
        let userId = "{{user_id}}";
        let minedAmount = {{user.mined}};
        let totalSpeed = {{speed}};

        setInterval(() => {
            if (totalSpeed > 0) {
                minedAmount += (totalSpeed / 3600);
                document.getElementById('display-mined').innerText = minedAmount.toFixed(6);
            }
        }, 1000);

        function switchPage(pageId, element) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            element.classList.add('active');
        }

        function changeWallet() {
            let selected = document.getElementById('wallet-selector').value;
            const wallets = {{wallets|tojson}};
            document.getElementById('wallet-address').innerText = wallets[selected];
            document.getElementById('hidden-currency').value = selected;
        }

        function buyMiner(minerId) {
            fetch(`/api/buy?id=${userId}&miner=${minerId}`)
            .then(res => res.json())
            .then(data => {
                if(data.status === "success") { location.reload(); } 
                else { alert(data.message); }
            });
        }

        function claimMined() {
            fetch(`/api/claim?id=${userId}`)
            .then(res => res.json())
            .then(data => {
                if(data.status === "success") { alert("تم تحويل الأرباح لرصيدك الكاش بنجاح!"); location.reload(); }
            });
        }

        function dailyReward() {
            alert("تم استلام المكافأة اليومية بنجاح! +0.10$ كاش.");
        }
    </script>
</body>
</html>
"""

# --- ممرّات التطبيق (Routes) ---
@app.route('/')
def index():
    uid = request.args.get('id', '1609075265')
    data = load_data()
    if uid not in data['users']:
        data['users'][uid] = {"balance": 5.0, "gems": 10, "mined": 0.0, "last_calc": time.time(), "miners": {}}
        save_data(data)
    
    user = data['users'][uid]
    speed = update_mining(user)
    save_data(data)
    return render_template_string(HTML_TEMPLATE, user=user, user_id=uid, wallets=WALLETS, miner_types=MINER_TYPES, speed=round(speed, 4), news_link=NEWS_CHANNEL_LINK)

@app.route('/api/buy')
def api_buy():
    uid = request.args.get('id')
    miner_id = request.args.get('miner')
    data = load_data()
    user = data['users'].get(uid)
    
    if not user or miner_id not in MINER_TYPES:
        return jsonify({"status": "error", "message": "بيانات خاطئة"})
        
    cost = MINER_TYPES[miner_id]["cost"]
    update_mining(user)
    
    if user["balance"] >= cost:
        user["balance"] = round(user["balance"] - cost, 4)
        if "miners" not in user or not isinstance(user["miners"], dict):
            user["miners"] = {}
        user["miners"][miner_id] = user["miners"].get(miner_id, 0) + 1
        save_data(data)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "رصيدك الكاش غير كافٍ لشراء هذا الجهاز!"})

@app.route('/api/claim')
def api_claim():
    uid = request.args.get('id')
    data = load_data()
    user = data['users'].get(uid)
    if user:
        update_mining(user)
        user["balance"] = round(user["balance"] + user["mined"], 6)
        user["mined"] = 0.0
        save_data(data)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/deposit', methods=['POST'])
def deposit():
    uid = request.form['user_id']
    currency = request.form['currency']
    file = request.files['file']
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ قبول وإيداع 10$", callback_data=f"approve_{uid}_10"),
        telebot.types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_{uid}")
    )
    # 🔴 يرسل طلبات الإيداع لقناتك المحددة مباشرة
    bot.send_photo(PAYMENT_CHANNEL_ID, file, caption=f"📥 **طلب إيداع جديد**\n\n👤 معرف المستخدم: `{uid}`\n🪙 العملة: `{currency}`", reply_markup=markup, parse_mode="Markdown")
    return "<h2 style='color:green; text-align:center; font-family:sans-serif; margin-top:50px; background:#111; padding:20px;'>✅ تم إرسال إثباتك بنجاح للأدمن، سيتم تحديث رصيدك فور المراجعة!</h2>"

# --- كود تحكم البوت والقبول التلقائي ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    url = f"https://apexwarlords-production.up.railway.app?id={uid}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("تشغيل لعبة التعدين 🚀", web_app=telebot.types.WebAppInfo(url=url)))
    bot.send_message(m.chat.id, "🎯 مرحبًا بك في بوت تعدين **Apex Warlords**!\n\nاضغط على الزر أدناه لفتح الميني آب وبدء شراء أجهزة التعدين وتوليد الأرباح الحية.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_admin_buttons(call):
    if call.from_user.id != OWNER_ID: return
    parts = call.data.split("_")
    action = parts[0]
    uid = parts[1]
    
    data = load_data()
    if uid not in data['users']: return

    if action == "approve":
        amount = float(parts[2])
        data['users'][uid]['balance'] += amount
        save_data(data)
        
        # إرسال رسالة نجاح للمستخدم
        bot.send_message(uid, f"🎉 تهانينا! تمت الموافقة على إيداعك وتمت إضافة **{amount}$** إلى حسابك.")
        
        # 🟢 تحديث الرسالة في قناة الإيداع وتوثيقها في قناة السحوبات/العمليات
        bot.edit_message_caption(call.message.caption + "\n\n🟢 **الحالة: تم قبول الإيداع بنجاح**", call.message.chat.id, call.message.message_id)
        bot.send_message(WITHDRAWAL_CHANNEL_ID, f"✅ **عملية ناجحة**\n\n👤 المستخدم: `{uid}`\n💰 تم شحن رصيده بـ: `{amount}$` بنجاح.")
        
    elif action == "reject":
        bot.send_message(uid, "❌ تم رفض طلب الإيداع الخاص بك، يرجى التواصل مع الدعم الفني وتأكيد التحويل.")
        bot.edit_message_caption(call.message.caption + "\n\n🔴 **الحالة: تم رفض هذا الإيداع**", call.message.chat.id, call.message.message_id)

# تشغيل البوت في مسار منفصل لمنع تجميد خادم الفلاسك
threading.Thread(target=lambda: bot.infinity_polling()).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

