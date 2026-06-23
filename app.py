import os
import json
import time
import threading
import html
from flask import Flask, render_template_string, request, jsonify
import telebot

app = Flask(__name__)

# --- 🔒 Threading Lock لحماية البيانات من التداخل ---
data_lock = threading.Lock()

# --- ⚙️ الإعدادات والتوكنات الرسمية للمشروع ---
TOKEN = "8895527275:AAFiM1ZbdyaTDuMs_zSXOGV6Lkyhqk_HdoY"
OWNER_ID = 1609075265  

# 🌐 رابط السيرفر الفعلي والنهائي على منصة ريلواي
WEB_APP_URL = "https://Apexwarlords-production.up.railway.app" 

bot = telebot.TeleBot(TOKEN, threaded=False)

# 📁 إدارة مسارات حفظ البيانات وضمان عدم ضياعها عند إعادة التشغيل
DATA_DIR = '/app/data' if os.path.exists('/app/data') else '.'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')

PAYMENT_CHANNEL_ID = "@Apex_payment1"     
WITHDRAWAL_CHANNEL_ID = "@lil_10l"       
NEWS_CHANNEL_LINK = "https://t.me/FasterPay_Official"   

# 💳 عناوين محافظ الإيداع الخاصة بك
WALLETS = {
    "USDT_BEP20": "0x0aae3b8ed565178c5224296429310959536a80b6",
    "USDT_TRC20": "TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni",
    "TON": "UQAO-l2K9qQtbHzLGiWyyGRtsaGBh0t82qHaa2GDMqq49Lp8"
}

# ⚡ قاعدة بيانات الأجهزة والترقيات المتاحة في المتجر
MINER_TYPES = {
    "doge": {"name": "DOGE Miner", "cost": 0.5, "speed": 0.0120, "tier": "STARTER", "color": "#cbd5e1", "icon": "🛰️"},
    "wif": {"name": "WIF Turbine", "cost": 2.5, "speed": 0.0463, "tier": "COMMON", "color": "#22c55e", "icon": "⚙️"},
    "pengu": {"name": "PENGU COLD", "cost": 5.0, "speed": 0.2894, "tier": "COMMON", "color": "#22c55e", "icon": "❄️"},
    "neiro": {"name": "NEIRO FOMO", "cost": 10.0, "speed": 1.3310, "tier": "RARE", "color": "#3b82f6", "icon": "🔮"},
    "popcat": {"name": "POPCAT PUMP", "cost": 25.0, "speed": 3.6169, "tier": "RARE", "color": "#3b82f6", "icon": "🧬"},
    "asteroid": {"name": "ASTEROID NODE", "cost": 50.0, "speed": 8.1019, "tier": "EPIC", "color": "#a855f7", "icon": "☄️"},
    "shib": {"name": "SHIB CORE", "cost": 100.0, "speed": 18.5185, "tier": "EPIC", "color": "#a855f7", "icon": "🌋"},
    "floki": {"name": "FLOKI RIG", "cost": 250.0, "speed": 57.7040, "tier": "EPIC", "color": "#a855f7", "icon": "⚔️"},
    "pepe": {"name": "PEPE Engine", "cost": 1000.0, "speed": 289.3519, "tier": "ELITE", "color": "#f97316", "icon": "🐸"},
    "mtonga": {"name": "MTONGA Reactor", "cost": 5000.0, "speed": 777.0000, "tier": "LEGENDARY", "color": "#ef4444", "icon": "👑"}
}

# 🎯 المهام المتاحة داخل التطبيق للمستخدمين كسب مكافآت منها
TASKS = {
    "task1": {"title": "الانضمام لقناة الأخبار الرئيسية 📢", "reward": 0.10, "link": "https://t.me/lS_3P"},
    "task2": {"title": "الانضمام لقناة الإثباتات والسحب 🧾", "reward": 0.15, "link": "https://t.me/lil_10l"},
    "task3": {"title": "متابعة حساب التمويل الخاص بنا 💵", "reward": 0.20, "link": "https://t.me/Apex_payment1"}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f: json.dump({"users": {}}, f)
        return {"users": {}}
    with open(DATA_FILE, 'r') as f: 
        try: return json.load(f)
        except json.JSONDecodeError: return {"users": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

def update_mining(user):
    now = time.time()
    last = user.get("last_calc", now)
    total_speed = 0.0100  # السرعة الافتراضية المجانية
    if "miners" in user and isinstance(user["miners"], dict):
        for m_id, count in user["miners"].items():
            if m_id in MINER_TYPES:
                total_speed += MINER_TYPES[m_id]["speed"] * count
    elapsed = now - last
    user["mined"] = user.get("mined", 0.0) + (total_speed * (elapsed / 3600.0))
    user["last_calc"] = now
    return total_speed

# --- 🚀 واجهة الويب الشاملة والفخمة بالكامل (بدون أي اختصارات) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Apex Mining Premium</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #030712; color: #f8fafc; margin: 0; padding-bottom: 120px; overflow-x: hidden; background-image: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #030712 70%); }
        
        .top-bar { display: flex; flex-direction: column; align-items: center; padding: 18px 15px; background: rgba(17, 24, 39, 0.7); border-bottom: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(24px); position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 30px rgba(0,0,0,0.5); }
        .logo-area { font-size: 28px; font-weight: 900; background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px; text-shadow: 0 0 25px rgba(56, 189, 248, 0.4); margin-bottom: 15px; }
        
        .stats-row { display: flex; width: 100%; justify-content: space-between; gap: 14px; }
        .stat-box { flex: 1; background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 14px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 16px; font-weight: 800; box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: 0.3s; }
        .stat-box.cash { color: #10b981; border-color: rgba(16, 185, 129, 0.3); text-shadow: 0 0 10px rgba(16,185,129,0.2); }
        .stat-box.speed { color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); text-shadow: 0 0 10px rgba(56,189,248,0.2); }
        
        .wallet-tab-box { flex: 1; background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 14px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 16px; font-weight: 800; box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: 0.3s; cursor: pointer; }
        .wallet-tab-box.deposit-tab { color: #10b981; border-color: rgba(16, 185, 129, 0.3); }
        .wallet-tab-box.deposit-tab.active { background: rgba(16, 185, 129, 0.12); border-color: #10b981; box-shadow: 0 0 15px rgba(16,185,129,0.25); }
        .wallet-tab-box.withdraw-tab { color: #ef4444; border-color: rgba(239, 68, 68, 0.3); }
        .wallet-tab-box.withdraw-tab.active { background: rgba(239, 68, 68, 0.12); border-color: #ef4444; box-shadow: 0 0 15px rgba(239,68,68,0.25); }
        
        .page { display: none; padding: 20px 15px; animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .page.active { display: block; }
        
        .miner-card { background: linear-gradient(145deg, rgba(26, 31, 46, 0.85) 0%, rgba(12, 16, 26, 0.95) 100%); border-radius: 24px; border: 1px solid rgba(255,255,255,0.06); padding: 16px; margin-bottom: 18px; position: relative; display: flex; align-items: center; gap: 14px; box-shadow: 0 12px 40px rgba(0,0,0,0.5); overflow: hidden; border-left: 5px solid var(--bar-color); transition: 0.3s; }
        .miner-card:hover { transform: translateY(-3px); border-color: var(--bar-color); }
        
        .miner-avatar-box { width: 70px; height: 70px; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.4) 100%); border: 2px solid var(--bar-color); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 34px; box-shadow: 0 0 15px var(--bar-color); flex-shrink: 0; position: relative; }
        
        .miner-info { display: flex; flex-direction: column; gap: 3px; flex-grow: 1; min-width: 0; }
        .miner-name { font-size: 17px; font-weight: 800; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .miner-meta { font-size: 11px; color: #9ca3af; }
        .miner-owned { font-size: 11px; color: #10b981; font-weight: bold; background: rgba(16,185,129,0.1); padding: 2px 8px; border-radius: 20px; width: fit-content; margin-top: 3px; border: 1px solid rgba(16,185,129,0.2); }
        
        .btn-buy { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #030712; border: none; font-weight: 900; padding: 12px 18px; border-radius: 14px; cursor: pointer; box-shadow: 0 6px 20px rgba(245, 158, 10, 0.3); font-size: 13px; transition: 0.2s; flex-shrink: 0; }
        
        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .reactor-core { width: 220px; height: 220px; position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; margin-top: 15px; }
        .reactor-sphere { width: 140px; height: 140px; background: radial-gradient(circle, #38bdf8 0%, #4f46e5 100%); border-radius: 50%; box-shadow: 0 0 60px rgba(56, 189, 248, 0.6); animation: pulse 2s infinite alternate; }
        .reactor-outer-ring { position: absolute; width: 190px; height: 190px; border: 2px dashed rgba(56, 189, 248, 0.4); border-radius: 50%; animation: rotateRing 10s linear infinite; }
        @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.08); } }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        .claim-panel { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); width: 100%; padding: 25px; border-radius: 28px; text-align: center; box-shadow: 0 10px 35px rgba(29, 78, 216, 0.4); cursor: pointer; margin-bottom: 25px; transition: 0.2s; border: 1px solid rgba(255,255,255,0.1); }
        .grid-menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 100%; }
        .grid-item { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 20px; text-align: center; cursor: pointer; font-weight: 700; transition: 0.2s; border: 1px solid rgba(255,255,255,0.03); }
        .grid-item:hover { background: rgba(255,255,255,0.06); }
        
        .section-card { background: linear-gradient(180deg, rgba(31,41,55,0.5) 0%, rgba(17,24,39,0.5) 100%); border: 1px solid rgba(255,255,255,0.07); border-radius: 26px; padding: 22px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        input, select { width: 100%; padding: 16px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; color: white; margin-top: 8px; margin-bottom: 18px; text-align: right; font-weight: 600; font-size: 15px; }
        label { font-size: 14px; font-weight: 700; color: #9ca3af; display: block; margin-right: 4px; }
        .btn-action { width: 100%; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; padding: 16px; border-radius: 14px; font-weight: 700; cursor: pointer; font-size: 16px; transition: 0.2s; }
        
        .address-box { background: rgba(0, 0, 0, 0.5); border: 1px dashed rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 14px; margin-bottom: 18px; text-align: center; }
        .btn-copy { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 14px; border-radius: 10px; font-size: 12px; font-weight: bold; cursor: pointer; margin-top: 8px; }

        .nav-bar { position: fixed; bottom: 20px; left: 4%; width: 92%; background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 14px 0; border-radius: 26px; backdrop-filter: blur(20px); z-index: 999; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        .nav-bar { position: fixed; bottom: 20px; left: 4%; width: 92%; background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 14px 0; border-radius: 26px; backdrop-filter: blur(20px); z-index: 999; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #6b7280; cursor: pointer; font-size: 12px; font-weight: 700; gap: 5px; transition: 0.3s; }
        .nav-item.active { color: #38bdf8; text-shadow: 0 0 15px rgba(56,189,248,0.4); }
        
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="logo-area">APEX MINING</div>
        <div class="stats-row">
            <div class="stat-box cash">💵 <span id="display-cash">{{user.balance}}</span> $</div>
            <div class="stat-box speed">⚡ <span>{{speed}} /س</span></div>
        </div>
    </div>

    <div id="page-main" class="page active">
        <div class="main-container">
            <div class="reactor-core">
                <div class="reactor-outer-ring"></div>
                <div class="reactor-sphere"></div>
            </div>
            <div class="claim-panel" onclick="claimMined()">
                <div style="font-size: 34px; font-weight: 900; color: #fff;"><span id="display-mined">0.000000</span></div>
                <div style="font-size: 14px; color: #93c5fd; margin-top: 6px; font-weight: 700;">اضغط لتجميع الأرباح المتولدة 🚀</div>
            </div>
            <div class="grid-menu">
                <div class="grid-item" onclick="dailyReward()" style="background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.25); color: #fbbf24;">🎁 المكافأة اليومية</div>
                <div class="grid-item" onclick="window.open('{{news_link}}')">📢 قناة الأخبار</div>
            </div>
        </div>
    </div>

    <div id="page-store" class="page">
        <h3 style="margin-top: 0; margin-bottom: 22px; text-align: center; color: #38bdf8; font-weight: 900; font-size: 22px;">ترقية ترسانة التعدين السحابي</h3>
        {% for m_id, m in miner_types.items() %}
        <div class="miner-card" style="--bar-color: {{m.color}}">
            <div class="miner-avatar-box">{{m.icon}}</div>
            <div class="miner-info">
                <span class="miner-name">{{m.name}} <small style="font-size: 9px; color: {{m.color}}">[{{m.tier}}]</small></span>
                <span class="miner-meta">السعر: <strong style="color: #fbbf24;">{{m.cost}}$</strong></span>
                <span class="miner-meta">معدل الهاش: <strong style="color: #38bdf8;">+{{m.speed}}/س</strong></span>
                <span class="miner-owned">المخزون المملوك: {{user.miners.get(m_id, 0)}}</span>
            </div>
            <button class="btn-buy" onclick="buyMiner('{{m_id}}')">تجهيز</button>
        </div>
        {% endfor %}
    </div>

    <div id="page-tasks" class="page">
        <div class="section-card">
            <h4 style="margin-top: 0; color: #38bdf8; margin-bottom: 8px;">🔗 نظام كسب الإحالات</h4>
            <p style="font-size: 13px; color: #9ca3af; margin-bottom: 14px;">شارك الرابط واحصل على مكافأة بقيمة <strong style="color: #10b981;">0.10$</strong> عن كل شخص يسجل من خلالك!</p>
            <input type="text" id="ref-url" value="{{invite_url}}" readonly style="text-align: left; font-size: 12px; background: rgba(0,0,0,0.5);">
            <button class="btn-action" onclick="copyRefLink()">نسخ رابط الإحالة</button>
            <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 14px; font-weight: bold;">
                <span>إجمالي الإحالات: 👤 {{user.get('ref_count', 0)}}</span>
                <span style="color: #10b981;">الأرباح: {{user.get('ref_earned', 0.0)}}$</span>
            </div>
        </div>

        <h4 style="color: #fff; margin-bottom: 12px;">المهام الحالية:</h4>
        {% for t_id, t in tasks_dict.items() %}
        <div class="miner-card" style="--bar-color: #4f46e5;">
            <div class="miner-info">
                <span style="font-weight: bold; font-size: 15px;">{{t.title}}</span>
                <span style="font-size: 12px; color: #10b981; font-weight: bold;">المكافأة: +{{t.reward}}$</span>
            </div>
            {% if t_id in user.get('completed_tasks', []) %}
            <button class="btn-buy" disabled style="background: #374151; color: #9ca3af;">مكتملة ✓</button>
            {% else %}
            <button class="btn-buy" style="background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: #fff;" onclick="startTask('{{t_id}}', '{{t.link}}')">ابدأ</button>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div id="page-wallet" class="page">
        <div class="stats-row" style="margin-bottom: 22px;">
            <div id="tab-deposit-btn" class="wallet-tab-box deposit-tab active" onclick="switchWalletForm('deposit')">📥 الإيداع (Deposit)</div>
            <div id="tab-withdraw-btn" class="wallet-tab-box withdraw-tab" onclick="switchWalletForm('withdraw')">📤 السحب (Withdraw)</div>
        </div>

        <div id="section-deposit" class="section-card" style="border-color: rgba(16, 185, 129, 0.2);">
            <h4 style="margin-top: 0; color: #10b981; margin-bottom: 8px;">📥 شحن الرصيد (Deposit)</h4>
            
            <label>اختر شبكة الإيداع المتوفرة:</label>
            <select id="deposit-method" onchange="onDepositNetworkChange()">
                <option value="">-- اضغط للاختيار وإظهار العنوان --</option>
                <option value="USDT_BEP20">USDT (BEP-20)</option>
                <option value="USDT_TRC20">USDT (TRC-20)</option>
                <option value="TON">TON (Telegram Network)</option>
            </select>

            <div id="deposit-address-container" class="address-box" style="display: none;">
                <strong id="deposit-address-text" style="word-break: break-all; color: #fff; font-size: 13px;"></strong><br>
                <button class="btn-copy" onclick="copyDepositAddress()">نسخ العنوان 📋</button>
            </div>

            <label>المبلغ الذي قمت بتحويله ($):</label>
            <input type="number" id="deposit-amount" placeholder="أدخل القيمة المحولة بدقة">

            <label>ادخل ال id او العنوان الذي قمت بالتحويل منو:</label>
            <input type="text" id="deposit-txid" placeholder="ضع هنا الـ ID أو عنوان محفظتك الشخصية">
            
            <button class="btn-action" style="background: linear-gradient(90deg, #10b981 0%, #059669 100%);" onclick="submitDeposit()">تأكيد وإرسال إثبات الإيداع</button>
        </div>

        <div id="section-withdraw" class="section-card" style="border-color: rgba(239, 68, 68, 0.2); display: none;">
            <h4 style="margin-top: 0; color: #ef4444; margin-bottom: 8px;">📤 طلب سحب فوري (Withdraw)</h4>
            
            <label>اختر شبكة السحب:</label>
            <select id="withdraw-method">
                <option value="USDT_BEP20">USDT (BEP-20)</option>
                <option value="USDT_TRC20">USDT (TRC-20)</option>
                <option value="TON">TON (Telegram Network)</option>
            </select>
            
            <label>عنوان محفظة الاستلام الخاصة بك:</label>
            <input type="text" id="withdraw-address" placeholder="ضع عنوان محفظتك هنا بعناية">
            
            <label>المبلغ المراد سحبه ($):</label>
            <input type="number" id="withdraw-amount" placeholder="الحد الأدنى لتقديم السحب هو 5$">
            
            <button class="btn-action" style="background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);" onclick="submitWithdrawal()">تقديم طلب السحب الرسمي</button>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active" onclick="switchPage('main', this)">🏠 <span>الرئيسية</span></div>
        <div class="nav-item" onclick="switchPage('store', this)">⚡ <span>المتجر</span></div>
        <div class="nav-item" onclick="switchPage('tasks', this)">🎯 <span>المهام</span></div>
        <div class="nav-item" onclick="switchPage('wallet', this)">💼 <span>المالية</span></div>
    </div>

    <script>
        const WALLETS_MAP = {
            "USDT_BEP20": "0x0aae3b8ed565178c5224296429310959536a80b6",
            "USDT_TRC20": "TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni",
            "TON": "UQAO-l2K9qQtbHzLGiWyyGRtsaGBh0t82qHaa2GDMqq49Lp8"
        };

        let minedAmount = {{user.mined}};
        let speedFactor = {{speed}} / 3600;

        setInterval(() => {
            minedAmount += speedFactor;
            document.getElementById('display-mined').innerText = minedAmount.toFixed(6);
        }, 1000);

        function switchPage(pageId, element) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            element.classList.add('active');
        }

        function switchWalletForm(type) {
            const depBtn = document.getElementById('tab-deposit-btn');
            const witBtn = document.getElementById('tab-withdraw-btn');
            const depSec = document.getElementById('section-deposit');
            const witSec = document.getElementById('section-withdraw');
            if(type === 'deposit') {
                depBtn.classList.add('active'); witBtn.classList.remove('active');
                depSec.style.display = 'block'; witSec.style.display = 'none';
            } else {
                witBtn.classList.add('active'); depBtn.classList.remove('active');
                witSec.style.display = 'block'; depSec.style.display = 'none';
            }
        }

        function onDepositNetworkChange() {
            let select = document.getElementById('deposit-method');
            let container = document.getElementById('deposit-address-container');
            let addrText = document.getElementById('deposit-address-text');
            if (select.value && WALLETS_MAP[select.value]) {
                addrText.innerText = WALLETS_MAP[select.value];
                container.style.display = 'block';
            } else { container.style.display = 'none'; }
        }

        function copyDepositAddress() {
            navigator.clipboard.writeText(document.getElementById('deposit-address-text').innerText);
            alert("تم نسخ عنوان المحفظة للمراد تحويلها!");
        }

        function claimMined() {
            fetch('/api/claim?id={{user_id}}').then(res => res.json()).then(data => {
                alert(data.message); if(data.status === "success") location.reload();
            });
        }

        function buyMiner(minerId) {
            fetch('/api/buy_miner?id={{user_id}}&miner_id=' + minerId).then(res => res.json()).then(data => {
                alert(data.message); if(data.status === "success") location.reload();
            });
        }

        function startTask(taskId, url) {
            window.open(url, '_blank');
            setTimeout(() => {
                fetch('/api/complete_task?id={{user_id}}&task_id=' + taskId).then(res => res.json()).then(data => {
                    alert(data.message); if(data.status === "success") location.reload();
                });
            }, 4000);
        }

        function copyRefLink() {
            let inputEl = document.getElementById('ref-url');
            inputEl.select(); navigator.clipboard.writeText(inputEl.value);
            alert("تم نسخ رابط إحالتك الفريد!");
        }

        function dailyReward() {
            fetch('/api/daily_reward?id={{user_id}}').then(res => res.json()).then(data => {
                alert(data.message); if(data.status === "success") location.reload();
            });
        }

        function submitDeposit() {
            let method = document.getElementById('deposit-method').value;
            let amount = document.getElementById('deposit-amount').value;
            let txid = document.getElementById('deposit-txid').value;
            if(!method || !amount || !txid) return alert("يرجى ملء جميع البيانات لإرسال طلب شحن الحساب!");
            fetch('/api/deposit?id={{user_id}}&method=' + method + '&amount=' + amount + '&txid=' + txid)
            .then(res => res.json()).then(data => {
                alert(data.message); if(data.status === "success") location.reload();
            });
        }

        function submitWithdrawal() {
            let method = document.getElementById('withdraw-method').value;
            let address = document.getElementById('withdraw-address').value;
            let amount = document.getElementById('withdraw-amount').value;
            if(!address || !amount) return alert("يرجى ملء جميع الخانات المخصصة للسحب!");
            fetch('/api/withdraw?id={{user_id}}&method=' + method + '&address=' + address + '&amount=' + amount)
            .then(res => res.json()).then(data => {
                alert(data.message); if(data.status === "success") location.reload();
            });
        }
    </script>
</body>
</html>
"""

# --- 🛰️ مسار استقبال البيانات الفوري عبر الـ Webhook بدون تداخل ---
@app.route(f'/{TOKEN}', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return jsonify({"status": "error"}), 403

# --- 🛰️ مسارات الـ API الخلفية للمشروع ---
@app.route('/')
def index():
    uid = request.args.get('id', '1609075265')
    invite_url = f"https://t.me/Apex_Warlordsbot?start=ref_{uid}"
    with data_lock:
        data = load_data()
        if uid not in data['users']:
            data['users'][uid] = {"balance": 0.0, "mined": 0.0, "last_calc": time.time(), "miners": {}, "last_reward": 0.0, "ref_count": 0, "ref_earned": 0.0, "completed_tasks": []}
        user = data['users'][uid]
        speed = update_mining(user)
        save_data(data)
    return render_template_string(HTML_TEMPLATE, user=user, user_id=uid, wallets=WALLETS, miner_types=MINER_TYPES, tasks_dict=TASKS, speed=round(speed, 4), invite_url=invite_url, news_link=NEWS_CHANNEL_LINK)

@app.route('/api/claim')
def api_claim():
    uid = request.args.get('id')
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if not user: return jsonify({"status": "error", "message": "فشل العثور على الحساب"})
        update_mining(user)
        mined = user.get("mined", 0.0)
        if mined < 0.01: return jsonify({"status": "error", "message": "الحد الأدنى للتجميع هو 0.01$"})
        user["balance"] = round(user.get("balance", 0.0) + mined, 4)
        user["mined"] = 0.0
        save_data(data)
    return jsonify({"status": "success", "message": f"تم تجميع {round(mined, 4)}$ ونقلها لرصيدك!"})

@app.route('/api/buy_miner')
def api_buy_miner():
    uid = request.args.get('id')
    m_id = request.args.get('miner_id')
    if m_id not in MINER_TYPES: return jsonify({"status": "error", "message": "جهاز غير صالح"})
    cost = MINER_TYPES[m_id]["cost"]
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if user.get("balance", 0.0) < cost: return jsonify({"status": "error", "message": "رصيدك غير كافٍ!"})
        user["balance"] = round(user["balance"] - cost, 4)
        if "miners" not in user: user["miners"] = {}
        user["miners"][m_id] = user["miners"].get(m_id, 0) + 1
        update_mining(user)
        save_data(data)
    return jsonify({"status": "success", "message": "تم التجهيز بنجاح! ⚡"})

@app.route('/api/complete_task')
def api_complete_task():
    uid = request.args.get('id')
    t_id = request.args.get('task_id')
    if t_id not in TASKS: return jsonify({"status": "error", "message": "المهمة غير موجودة"})
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if "completed_tasks" not in user: user["completed_tasks"] = []
        if t_id in user["completed_tasks"]: return jsonify({"status": "error", "message": "أتممتها بالفعل!"})
        user["completed_tasks"].append(t_id)
        user["balance"] = round(user.get("balance", 0.0) + TASKS[t_id]["reward"], 4)
        save_data(data)
    return jsonify({"status": "success", "message": "تم التحقق وإضافة المكافأة!"})

@app.route('/api/daily_reward')
def api_daily_reward():
    uid = request.args.get('id')
    now = time.time()
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        last_reward = user.get("last_reward", 0.0)
        if now - last_reward >= 86400:
            user["balance"] = round(user.get("balance", 0.0) + 0.10, 4)
            user["last_reward"] = now
            save_data(data)
            return jsonify({"status": "success", "message": "تم استلام المكافأة اليومية (+0.10$)!"})
        return jsonify({"status": "error", "message": "عد لاحقاً بعد انتهاء الـ 24 ساعة."})

@app.route('/api/deposit')
def api_deposit():
    uid = request.args.get('id')
    method = request.args.get('method')
    amount = request.args.get('amount')
    txid = request.args.get('txid')
    
    safe_uid = html.escape(str(uid)) if uid else "None"
    safe_amount = html.escape(str(amount)) if amount else "0"
    safe_method = html.escape(str(method)) if method else "None"
    safe_txid = html.escape(str(txid)) if txid else "None"
    
    msg = (
        f"📥 <b>NEW DEPOSIT PROOF SUBMITTED</b>\n\n"
        f"👤 <b>User ID:</b> <code>{safe_uid}</code>\n"
        f"💰 <b>Amount:</b> {safe_amount}$\n"
        f"🛡️ <b>Network Chosen:</b> {safe_method}\n"
        f"📌 <b>Sender Info / Account:</b>\n<code>{safe_txid}</code>"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("✅ Approve & Deposit", callback_data=f"dep_a_{safe_uid}_{safe_amount}"),
        telebot.types.InlineKeyboardButton("❌ Reject Request", callback_data=f"dep_r_{safe_uid}_{safe_amount}")
    )
    
    try:
        bot.send_message(PAYMENT_CHANNEL_ID, msg, parse_mode="HTML", reply_markup=markup)
        bot.send_message(OWNER_ID, msg, parse_mode="HTML", reply_markup=markup)
    except Exception as e: print(f"Error channel deposit: {e}")
    
    return jsonify({"status": "success", "message": "تم إرسال إثبات الإيداع بنجاح للمراجعة!"})

@app.route('/api/withdraw')
def api_withdraw():
    uid = request.args.get('id')
    method = request.args.get('method')
    addr = request.args.get('address')
    amount = float(request.args.get('amount', 0))
    
    if amount < 5.0: return jsonify({"status": "error", "message": "الحد الأدنى للسحب هو 5$!"})
    
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if user.get("balance", 0.0) < amount: return jsonify({"status": "error", "message": "رصيدك الحالي غير كافٍ!"})
        user["balance"] = round(user["balance"] - amount, 4)
        save_data(data)
        
    safe_uid = html.escape(str(uid)) if uid else "None"
    safe_method = html.escape(str(method)) if method else "None"
    safe_addr = html.escape(str(addr)) if addr else "None"
        
    msg = (
        f"📤 <b>NEW WITHDRAWAL REQUEST PENDING</b>\n\n"
        f"👤 <b>User ID:</b> <code>{safe_uid}</code>\n"
        f"💰 <b>Requested Amount:</b> {amount}$\n"
        f"🛡️ <b>Network System:</b> {safe_method}\n"
        f"📌 <b>Destination Wallet Address:</b>\n<code>{safe_addr}</code>"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("✅ Approve & Pay", callback_data=f"wit_a_{safe_uid}_{amount}"),
        telebot.types.InlineKeyboardButton("❌ Reject & Refund", callback_data=f"wit_r_{safe_uid}_{amount}")
    )
    
    try:
        bot.send_message(WITHDRAWAL_CHANNEL_ID, msg, parse_mode="HTML", reply_markup=markup)
        bot.send_message(OWNER_ID, msg, parse_mode="HTML", reply_markup=markup)
    except Exception as e: print(f"Error channel withdraw: {e}")
    
    return jsonify({"status": "success", "message": "تم تقديم طلب السحب بنجاح!"})

# --- ⚙️ معالجة الأزرار التفاعلية وتأمين النقرات للمالك فقط ---

@bot.callback_query_handler(func=lambda call: True)
def handle_admin_buttons(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ عذراً يا غالي! هذه الصلاحية محجوزة لمالك البوت الأصلي فقط.", show_alert=True)
        return

    parts = call.data.split('_')
    if len(parts) < 4: return
        
    action_type = parts[0]
    status = parts[1]
    target_uid = parts[2]
    amount = float(parts[3])
    
    status_msg = ""
    
    with data_lock:
        data = load_data()
        user = data['users'].get(target_uid)
        
        if action_type == "dep":
            if status == "a":
                if user:
                    user["balance"] = round(user.get("balance", 0.0) + amount, 4)
                    status_msg = f"\n\n🟢 <b>Status: APPROVED (+{amount}$ added)</b>"
                    try: bot.send_message(int(target_uid), f"🎉 تم تأكيد إيداعك بنجاح! تم إضافة {amount}$ إلى حسابك.")
                    except: pass
            else:
                status_msg = f"\n\n🔴 <b>Status: REJECTED (Proof Denied)</b>"
                try: bot.send_message(int(target_uid), f"❌ تم رفض إثبات الإيداع الخاص بك بقيمة {amount}$.")
                except: pass
                
        elif action_type == "wit":
            if status == "a":
                status_msg = f"\n\n🟢 <b>Status: APPROVED & PAID ({amount}$)</b>"
                try: bot.send_message(int(target_uid), f"✅ تم معالجة طلب سحبك بقيمة {amount}$ بنجاح!")
                except: pass
            else:
                if user: user["balance"] = round(user.get("balance", 0.0) + amount, 4)
                status_msg = f"\n\n🔴 <b>Status: REJECTED & REFUNDED</b>"
                try: bot.send_message(int(target_uid), f"❌ تم رفض طلب سحبك بقيمة {amount}$ وتم إعادة الأموال لرصيدك.")
                except: pass
                
        save_data(data)

    try:
        updated_text = call.message.text + status_msg
        bot.edit_message_text(updated_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None, parse_mode="HTML")
        bot.answer_callback_query(call.id, "تم تحديث المعاملة بنجاح!", show_alert=False)
    except Exception as e: print(f"Error editing text response: {e}")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = str(message.from_user.id)
    text_split = message.text.split()
    with data_lock:
        data = load_data()
        if uid not in data['users']:
            data['users'][uid] = {"balance": 0.0, "mined": 0.0, "last_calc": time.time(), "miners": {}, "last_reward": 0.0, "ref_count": 0, "ref_earned": 0.0, "completed_tasks": []}
            if len(text_split) > 1 and text_split[1].startswith('ref_'):
                referrer_id = text_split[1].replace('ref_', '').strip()
                if referrer_id in data['users'] and referrer_id != uid:
                    ref_user = data['users'][referrer_id]
                    ref_user["ref_count"] = ref_user.get("ref_count", 0) + 1
                    ref_user["ref_earned"] = round(ref_user.get("ref_earned", 0.0) + 0.10, 4)
                    ref_user["balance"] = round(ref_user.get("balance", 0.0) + 0.10, 4)
                    try: bot.send_message(int(referrer_id), f"👤 New referral linked. <b>+0.10$</b> credited!", parse_mode="HTML")
                    except: pass
        save_data(data)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 Launch Apex Mining Terminal", web_app=telebot.types.WebAppInfo(url=f"{WEB_APP_URL}/?id={uid}")))
    bot.reply_to(message, f"🔥 <b>Welcome to Apex Cloud Mining Premium!</b>\n\n👇 <b>Tap the action button to launch app:</b>", parse_mode="HTML", reply_markup=markup)

# --- ⚙️ إعداد وتنشيط الـ Webhook التلقائي الآمن ---
def set_webhook():
    time.sleep(3)
    try:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEB_APP_URL}/{TOKEN}")
        print("✅ Telegram Webhook set successfully!")
    except Exception as e:
        print(f"❌ Webhook configuration failed: {e}")

threading.Thread(target=set_webhook, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

