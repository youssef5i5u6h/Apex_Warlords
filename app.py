import os
import json
import time
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot

app = Flask(__name__)

# --- ⚙️ الإعدادات الأساسية وقنوات التليجرام الخاصة بك ---
TOKEN = "8895527275:AAGg5nDAdS2O2NKDX8IAjcPt7Dknz9CgpL4"
OWNER_ID = 1609075265  # لو الزرار قالك الـ ID بتاعك مختلف، غير الرقم ده بالرقم اللي هيظهرلك
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

# --- الواجهة الفخمة والحديثة بالكامل ---
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
        
        .top-bar { display: flex; flex-direction: column; align-items: center; padding: 18px 15px; background: rgba(10, 15, 30, 0.7); border-bottom: 1px solid rgba(255, 255, 255, 0.06); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); position: sticky; top: 0; z-index: 1000; }
        .logo-area { font-size: 26px; font-weight: 900; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px; text-shadow: 0 0 20px rgba(0, 242, 254, 0.3); margin-bottom: 15px; }
        .stats-row { display: flex; width: 100%; justify-content: space-between; gap: 14px; }
        .stat-box { flex: 1; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 16px; font-weight: 800; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: 0.3s; }
        .stat-box.cash { color: #10b981; border-color: rgba(16, 185, 129, 0.25); background: linear-gradient(180deg, rgba(16,185,129,0.05) 0%, rgba(0,0,0,0) 100%); }
        .stat-box.gems { color: #00f2fe; border-color: rgba(0, 242, 254, 0.25); background: linear-gradient(180deg, rgba(0,242,254,0.05) 0%, rgba(0,0,0,0) 100%); }

        .page { display: none; padding: 20px 15px; animation: slideUp 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
        .page.active { display: block; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

        .miner-card { background: linear-gradient(145deg, rgba(20, 28, 47, 0.9) 0%, rgba(11, 16, 28, 0.9) 100%); border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); padding: 18px; margin-bottom: 16px; position: relative; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.4); overflow: hidden; transition: 0.2s; }
        .miner-card:active { transform: scale(0.98); border-color: rgba(255,255,255,0.15); }
        .miner-info { display: flex; flex-direction: column; gap: 6px; }
        .miner-name { font-size: 19px; font-weight: 800; color: #fff; letter-spacing: 0.5px; }
        .miner-tier { position: absolute; top: 14px; left: 18px; font-size: 9px; font-weight: 900; padding: 4px 10px; border-radius: 30px; letter-spacing: 1px; background: rgba(255,255,255,0.05); }
        .miner-speed { font-size: 12px; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 5px 12px; border-radius: 10px; display: inline-block; width: fit-content; font-weight: 700; border: 1px solid rgba(56, 189, 248, 0.15); }
        .miner-owned { font-size: 13px; color: #f59e0b; font-weight: 700; margin-top: 2px; }
        .btn-buy { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #05070f; border: none; font-weight: 900; padding: 14px 24px; border-radius: 16px; cursor: pointer; box-shadow: 0 6px 20px rgba(217, 119, 6, 0.3); font-size: 14px; transition: 0.2s; }
        .btn-buy:active { transform: scale(0.92); box-shadow: none; }

        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .reactor-core { width: 200px; height: 200px; position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; }
        .reactor-sphere { width: 130px; height: 130px; background: radial-gradient(circle, #00f2fe 0%, #1d4ed8 100%); border-radius: 50%; box-shadow: 0 0 50px rgba(0, 242, 254, 0.6), inset 0 0 20px rgba(255,255,255,0.6); animation: pulse 2s infinite alternate cubic-bezier(0.4, 0, 0.6, 1); z-index: 2; }
        .reactor-outer-ring { position: absolute; width: 170px; height: 170px; border: 2px dashed rgba(0, 242, 254, 0.3); border-radius: 50%; animation: rotateRing 8s linear infinite; }
        @keyframes pulse { from { transform: scale(1); box-shadow: 0 0 35px rgba(0, 242, 254, 0.5); } to { transform: scale(1.08); box-shadow: 0 0 60px rgba(0, 242, 254, 0.9); } }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        .claim-panel { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); width: 100%; padding: 22px; border-radius: 24px; text-align: center; box-shadow: 0 8px 30px rgba(29, 78, 216, 0.4); cursor: pointer; margin-bottom: 25px; border: 1px solid #3b82f6; transition: 0.2s; }
        .claim-panel:active { transform: scale(0.97); box-shadow: 0 4px 15px rgba(29, 78, 216, 0.2); }
        .claim-amount { font-size: 32px; font-weight: 900; color: #fff; text-shadow: 0 2px 10px rgba(0,0,0,0.3); font-family: 'Courier New', Courier, monospace; letter-spacing: 0.5px; }
        .claim-label { font-size: 14px; color: #93c5fd; font-weight: 700; margin-top: 6px; }

        .grid-menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 100%; }
        .grid-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 18px; text-align: center; cursor: pointer; font-weight: 700; font-size: 15px; transition: 0.2s; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .grid-item:active { background: rgba(255,255,255,0.08); transform: translateY(1px); }

        .wallet-tabs { display: flex; gap: 12px; margin-bottom: 25px; background: rgba(0,0,0,0.3); padding: 6px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.04); }
        .w-tab { flex: 1; padding: 14px; text-align: center; border-radius: 12px; font-weight: 800; cursor: pointer; color: #64748b; transition: 0.25s; }
        .w-tab.active { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: #fff; box-shadow: 0 4px 15px rgba(29, 78, 216, 0.3); }

        .input-select { width: 100%; padding: 16px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); color: #fff; border-radius: 16px; font-weight: 700; margin-bottom: 18px; font-size: 15px; outline: none; transition: 0.3s; }
        .input-select:focus { border-color: #3b82f6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.2); }
        .address-box { background: #02040a; border: 1px dashed rgba(59, 130, 246, 0.4); padding: 16px; border-radius: 16px; font-size: 14px; word-break: break-all; text-align: center; color: #00f2fe; margin-bottom: 18px; font-family: monospace; font-weight: bold; }
        
        .btn-action { background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white; border: none; padding: 16px; width: 100%; font-weight: 800; border-radius: 16px; cursor: pointer; box-shadow: 0 6px 20px rgba(29, 78, 216, 0.3); font-size: 16px; transition: 0.2s; }
        .btn-action:active { transform: scale(0.98); box-shadow: none; }
        
        .task-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 18px; border-radius: 20px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
        .task-btn { background: #2563eb; border: none; color: white; padding: 12px 24px; border-radius: 12px; font-weight: 800; font-size: 14px; cursor: pointer; transition: 0.2s; }
        .task-btn:active { transform: scale(0.93); }

        .nav-bar { position: fixed; bottom: 20px; left: 4%; width: 92%; background: rgba(15, 22, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 10px 0; border-radius: 24px; box-shadow: 0 10px 35px rgba(0,0,0,0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); z-index: 999; }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; color: #64748b; cursor: pointer; flex: 1; font-size: 11px; font-weight: 800; transition: 0.2s; }
        .nav-item.active { color: #00f2fe; filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.5)); }
        .nav-icon { font-size: 24px; margin-bottom: 2px; transition: 0.2s; }
        .nav-item:active .nav-icon { transform: scale(0.85); }
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
                <div class="claim-amount"><span id="display-mined">0.000000</span></div>
                <div class="claim-label">اضغط لتجميع الأرباح المتولدة الحالية 🚀</div>
            </div>
            <div class="grid-menu">
                <div class="grid-item" onclick="dailyReward()">🎁 مكافأة يومية</div>
                <div class="grid-item" onclick="window.open('{{news_link}}')">📢 قناة الأخبار</div>
            </div>
        </div>
    </div>

    <div id="page-miners" class="page">
        <p style="text-align: center; color: #94a3b8; font-size: 15px; margin-bottom: 20px;">سرعة التعدين الكلية الحالية: <span id="display-speed" style="color:#00f2fe; font-weight:900;">{{speed}}</span> H/S</p>
        {% for m_id, m in miner_types.items() %}
        <div class="miner-card">
            <div class="miner-info">
                <span class="miner-tier" style="color: {{m.color}}; border: 1px solid {{m.color}};">{{m.tier}}</span>
                <span class="miner-name">{{m.name}}</span>
                <span class="miner-speed">⚡ {{m.speed}} H/S</span>
                <span class="miner-owned">الكمية المملوكة: {{user.miners[m_id] or 0}}</span>
            </div>
            <button class="btn-buy" onclick="buyMiner('{{m_id}}')">شراء<br>{{m.cost}}$</button>
        </div>
        {% endfor %}
    </div>

    <div id="page-tasks" class="page">
        <div class="task-card">
            <div>
                <div style="font-weight:800; font-size:15px;">انضم لقناة الإيداعات الرسمية لإثباتات الشحن</div>
                <div style="font-size:13px; color:#38bdf8; margin-top:4px;">المكافأة: +0.05$ | +5💎</div>
            </div>
            <button class="task-btn" onclick="window.open('https://t.me/Apex_payment1')">انضمام</button>
        </div>
        <div class="task-card">
            <div>
                <div style="font-weight:800; font-size:15px;">انضم لقناة السحوبات والعمليات الناجحة للعملاء</div>
                <div style="font-size:13px; color:#38bdf8; margin-top:4px;">المكافأة: +0.05$ | +5💎</div>
            </div>
            <button class="task-btn" onclick="window.open('https://t.me/lil_10l')">انضمام</button>
        </div>
        <div class="task-card">
            <div>
                <div style="font-weight:800; font-size:15px;">قم بتشغيل بوت DoodlePlay الرسمي</div>
                <div style="font-size:13px; color:#38bdf8; margin-top:4px;">المكافأة: +0.01$ | +1💎</div>
            </div>
            <button class="task-btn" onclick="window.open('https://t.me/DoodlePlayBot')">فتح</button>
        </div>
        <div class="task-card">
            <div>
                <div style="font-weight:800; font-size:15px;">انضم لقناة التحديثات والأخبار الكبيرة للمشروع</div>
                <div style="font-size:13px; color:#38bdf8; margin-top:4px;">المكافأة: +0.02$ | +2💎</div>
            </div>
            <button class="task-btn" onclick="window.open('{{news_link}}')">انضمام</button>
        </div>
    </div>

    <div id="page-friends" class="page" style="text-align:center; padding-top:15px;">
        <h3 style="color:#00f2fe; font-size: 22px;">دعوة الأصدقاء 👥</h3>
        <p style="color:#94a3b8; font-size:15px; line-height:1.6; margin-bottom: 20px;">قم بنسخ رابط الإحالة الخاص بك وتحصّل على 10% من أرباح أصدقائك فوراً عند قيامهم بالتجميع!</p>
        <div class="address-box">https://t.me/YourBotName_Bot?start={{user_id}}</div>
        <button class="btn-action" onclick="navigator.clipboard.writeText('https://t.me/YourBotName_Bot?start={{user_id}}'); alert('تم نسخ رابط الإحالة الخاص بك بنجاح!');">نسخ الرابط الفريد</button>
    </div>

    <div id="page-wallet" class="page">
        <div class="wallet-tabs">
            <div id="tab-deposit" class="w-tab active" onclick="toggleWalletSection('deposit')">💳 إيداع وشحن</div>
            <div id="tab-withdraw" class="w-tab" onclick="toggleWalletSection('withdraw')">💸 سحب الأرباح</div>
        </div>

        <div id="section-deposit" style="background: rgba(20, 28, 47, 0.4); padding:22px; border-radius:24px; border:1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px);">
            <h3 style="margin-top:0; text-align:center; color:#00f2fe;">شحن الحساب والإيداع</h3>
            <p style="color:#94a3b8; font-size:14px; text-align:center; margin-bottom:20px;">قم بالتحويل للمحفظة بالأسفل ثم اكتب المبلغ واضغط تأكيد المعاملة.</p>
            
            <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">اختر العملة الرقمية:</label>
            <select class="input-select" id="wallet-selector" onchange="changeWallet()">
                <option value="USDT_BEP20">USDT (BEP20)</option>
                <option value="USDT_TRC20">USDT (TRC20)</option>
                <option value="TON">TON Coin</option>
            </select>
            
            <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">عنوان محفظة الاستقبال الخاص بنا:</label>
            <div class="address-box" id="wallet-address">{{wallets['USDT_BEP20']}}</div>
            
            <form action="/deposit" method="post" style="margin-top:20px;">
                <input type="hidden" name="user_id" value="{{user_id}}">
                <input type="hidden" name="currency" id="hidden-currency" value="USDT_BEP20">
                
                <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">المبلغ الذي قمت بتحويله ($):</label>
                <input type="number" name="amount" class="input-select" placeholder="مثال: 10" required min="1">
                
                <button type="submit" class="btn-action">تأكيد وإرسال للتحقق</button>
            </form>
        </div>

        <div id="section-withdraw" style="background: rgba(20, 28, 47, 0.4); padding:22px; border-radius:24px; border:1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px); display:none;">
            <h3 style="margin-top:0; text-align:center; color:#10b981;">سحب الأموال والأرباح</h3>
            <p style="color:#94a3b8; font-size:14px; text-align:center; margin-bottom:20px;">اسحب أرباحك مباشرة إلى محفظتك الشخصية بكل سهولة وأمان.</p>
            
            <form action="/withdraw" method="post">
                <input type="hidden" name="user_id" value="{{user_id}}">
                
                <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">اختر شبكة السحب:</label>
                <select class="input-select" name="currency">
                    <option value="USDT_BEP20">USDT (BEP20)</option>
                    <option value="USDT_TRC20">USDT (TRC20)</option>
                    <option value="TON">TON Coin</option>
                </select>
                
                <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">عنوان محفظتك الشخصية للاستلام:</label>
                <input type="text" name="user_address" class="input-select" placeholder="أدخل عنوان محفظتك هنا بدقة" required>
                
                <label style="font-size:14px; font-weight:bold; display:block; margin-bottom:8px;">المبلغ المراد سحبه ($):</label>
                <input type="number" name="amount" class="input-select" placeholder="الحد الأدنى للسحب 10$" required min="10" step="any">
                
                <button type="submit" class="btn-action" style="background: linear-gradient(90deg, #10b981, #059669); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);">تأكيد طلب السحب الفوري</button>
            </form>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active" onclick="switchPage('main', this)"><span class="nav-icon">🏠</span>الرئيسية</div>
        <div class="nav-item" onclick="switchPage('miners', this)"><span class="nav-icon">⛏️</span>المعدنون</div>
        <div class="nav-item" onclick="switchPage('tasks', this)"><span class="nav-icon">📋</span>المهام</div>
        <div class="nav-item" onclick="switchPage('friends', this)"><span class="nav-icon">👥</span>الأصدقاء</div>
        <div class="nav-item" onclick="switchPage('wallet', this)"><span class="nav-icon">💳</span>المحفظة</div>
    </div>

    <script>
        let userId = "{{user_id}}";
        let minedAmount = Number("{{user.mined}}");
        let totalSpeed = Number("{{speed}}");

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

        function toggleWalletSection(type) {
            if(type === 'deposit') {
                document.getElementById('section-deposit').style.display = 'block';
                document.getElementById('section-withdraw').style.display = 'none';
                document.getElementById('tab-deposit').classList.add('active');
                document.getElementById('tab-withdraw').classList.remove('active');
            } else {
                document.getElementById('section-deposit').style.display = 'none';
                document.getElementById('section-withdraw').style.display = 'block';
                document.getElementById('tab-deposit').classList.remove('active');
                document.getElementById('tab-withdraw').classList.add('active');
            }
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
                if(data.status === "success") { alert("تم تحويل الأرباح لرصيدك الكاش بنجاح! 🔥"); location.reload(); }
            });
        }

        function dailyReward() {
            alert("تم استلام المكافأة اليومية الملكية بنجاح! +0.10$ كاش.");
        }
    </script>
</body>
</html>
"""

# --- ممرّات التطبيق المعززة بحماية ذكية ضد الانهيار ---
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
    amount = request.form.get('amount', '10')
    
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(f"✅ قبول وإيداع {amount}$", callback_data=f"approve_{uid}_{amount}"),
            telebot.types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_{uid}")
        )
        
        text = f"📥 **طلب إيداع جديد (تأكيد يدوي)**\n\n👤 معرف المستخدم: `{uid}`\n🪙 العملة المستخدمة: `{currency}`\n💰 المبلغ المذكور: `{amount}$`"
        bot.send_message(PAYMENT_CHANNEL_ID, text, reply_markup=markup, parse_mode="Markdown")
        
        return """
        <body style="background:#05070f; color:#fff; font-family:sans-serif; text-align:center; padding-top:100px;">
            <div style="background: rgba(20, 28, 47, 0.6); backdrop-filter: blur(15px); max-width:400px; margin:0 auto; padding:40px; border-radius:24px; border:1px solid rgba(255,255,255,0.06); box-shadow:0 10px 30px rgba(0,0,0,0.5);">
                <h2 style="color:#f59e0b; margin-bottom:15px; font-weight:900;">⏳ معالجة الطلب الآمن</h2>
                <p style="color:#94a3b8; line-height:1.7; font-size:15px;">لقد تم إرسال تفاصيل معاملتك المالية للتحقق اليدوي بنجاح. سيتم مراجعة طلبك وإضافة الرصيد لحسابك بشكل تلقائي وفوري فور التأكيد.</p>
                <br>
                <a href="javascript:history.back()" style="display:inline-block; background: linear-gradient(90deg, #2563eb, #1d4ed8); color:#fff; text-decoration:none; padding:14px 30px; border-radius:12px; font-weight:bold; font-size:14px; box-shadow:0 4px 15px rgba(29,78,216,0.3);">العودة للتطبيق</a>
            </div>
        </body>
        """
    except Exception as e:
        return f"""
        <body style="background:#05070f; color:#fff; font-family:sans-serif; text-align:center; padding-top:80px;">
            <div style="background:rgba(20,28,47,0.6); backdrop-filter:blur(15px); max-width:480px; margin:0 auto; padding:40px; border-radius:24px; border:1px solid #ef4444; box-shadow:0 10px 30px rgba(0,0,0,0.5);">
                <h2 style="color:#ef4444; font-weight:900; margin-bottom:15px;">❌ خطأ في إعدادات السيرفر والإرساال</h2>
                <p style="color:#94a3b8; line-height:1.7; font-size:15px;">فشل السيرفر في إرسال إشعار الإيداع إلى القناة الإدارية الخاصة بك.</p>
                <br>
                <a href="javascript:history.back()" style="display:inline-block; background:#ef4444; color:#fff; text-decoration:none; padding:12px 25px; border-radius:12px; font-weight:bold;">العودة وتعديل القناة</a>
            </div>
        </body>
        """

@app.route('/withdraw', methods=['POST'])
def withdraw():
    uid = request.form['user_id']
    currency = request.form['currency']
    user_address = request.form['user_address']
    amount = float(request.form.get('amount', '10'))
    
    data = load_data()
    user = data['users'].get(uid)
    
    if not user: return "خطأ في بيانات العميل"
    if user["balance"] < amount: return "رصيد غير كافٍ"
    
    try:
        user["balance"] = round(user["balance"] - amount, 4)
        save_data(data)
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(f"✅ تم الإرسال والموافقة", callback_data=f"wapprove_{uid}_{amount}"),
            telebot.types.InlineKeyboardButton("❌ رفض وإرجاع الرصيد", callback_data=f"wreject_{uid}_{amount}")
        )
        
        text = f"💸 **طلب سحب جديد قيد التنفيذ**\n\n👤 معرف العميل: `{uid}`\n🪙 العملة والشبكة: `{currency}`\n📥 عنوان محفظة العميل: `{user_address}`\n💰 القيمة المطلوبة: `{amount}$`"
        bot.send_message(WITHDRAWAL_CHANNEL_ID, text, reply_markup=markup, parse_mode="Markdown")
        
        return "تم تسجيل طلب السحب بنجاح جاري المعالجة."
    except Exception as e:
        user["balance"] = round(user["balance"] + amount, 4)
        save_data(data)
        return "فشل السحب، تأكد من صلاحيات البوت في القناة."

# --- 🔐 معالج أزرار القنوات المتطور والخالي من التعليق ---
@bot.callback_query_handler(func=lambda call: True)
def handle_admin_buttons(call):
    # 1. فك تعليق زرار التليجرام فوراً وبشكل لحظي من السيرفر
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass
        
    # 2. التحقق الذكي من رتبة وصلاحية الشخص الضاغط على الزرار
    if call.from_user.id != OWNER_ID:
        try:
            bot.send_message(call.message.chat.id, f"⚠️ تنبيه حماية: الحساب الخاص بك ليس المالك المعين للبوت!\n👤 الـ ID الخاص بك: `{call.from_user.id}`\n\n💡 إذا كنت أنت المالك، انسخ هذا الرقم واستبدله بالـ `OWNER_ID` في سطر الكود رقم 9.")
        except Exception:
            pass
        return
        
    parts = call.data.split("_")
    action = parts[0]
    uid = parts[1]
    
    data = load_data()
    if uid not in data['users']:
        try: bot.send_message(call.message.chat.id, "❌ خطأ: حساب المستخدم هذا لم يعد متواجداً في ملف الـ JSON.")
        except Exception: pass
        return

    try:
        if action == "approve":
            amount = float(parts[2])
            data['users'][uid]['balance'] = round(data['users'][uid]['balance'] + amount, 4)
            save_data(data)
            
            try: bot.send_message(uid, f"🎉 تهانينا! تمت الموافقة على إيداعك وتمت إضافة **{amount}$** إلى رصيدك الكاش بنجاح.")
            except Exception: pass
            
            bot.edit_message_text(call.message.text + f"\n\n🟢 **الحالة: تم قبول الإيداع وإضافة {amount}$**", call.message.chat.id, call.message.message_id)
            
        elif action == "reject":
            try: bot.send_message(uid, "❌ تم رفض طلب الإيداع الخاص بك من قِبل الإدارة، يرجى مراجعة الدعم وتأكيد بيانات التحويل.")
            except Exception: pass
            bot.edit_message_text(call.message.text + "\n\n🔴 **الحالة: تم رفض الطلب**", call.message.chat.id, call.message.message_id)

        elif action == "wapprove":
            amount = float(parts[2])
            try: bot.send_message(uid, f"✅ تم تحويل وإرسال مبلغ السحب بقيمة **{amount}$** لمحفظتك بنجاح برقم المعاملة الخاص بك!")
            except Exception: pass
            bot.edit_message_text(call.message.text + f"\n\n🟢 **الحالة: تم التحويل بنجاح للمستخدم والموافقة**", call.message.chat.id, call.message.message_id)
            
        elif action == "wreject":
            amount = float(parts[2])
            data['users'][uid]['balance'] = round(data['users'][uid]['balance'] + amount, 4)
            save_data(data)
            try: bot.send_message(uid, f"❌ تم رفض طلب السحب الخاص بك بقيمة **{amount}$** من قِبل الإدارة وتم إرجاع المبلغ كاملاً لرصيدك الكاش.")
            except Exception: pass
            bot.edit_message_text(call.message.text + f"\n\n🔴 **الحالة: تم رفض السحب وإعادة الأموال للحساب**", call.message.chat.id, call.message.message_id)
            
    except Exception as e:
        try: bot.send_message(call.message.chat.id, f"❌ حدث خطأ برمجي داخلي: {str(e)}")
        except Exception: pass

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    url = f"https://apexwarlords-production.up.railway.app?id={uid}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Launch Apex Mining 🚀", web_app=telebot.types.WebAppInfo(url=url)))
    bot.send_message(m.chat.id, "🎯 Welcome to **Apex Mining Premium**!", reply_markup=markup, parse_mode="Markdown")

# تشغيل الـ Polling الآمن في الخلفية
threading.Thread(target=lambda: bot.infinity_polling(timeout=10, long_polling_timeout=5)).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

