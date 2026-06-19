import os
import random
import threading
from flask import Flask, render_template_string, request, jsonify
import telebot
from telebot import types

app = Flask(__name__)

# 🔐 توكن البوت الخاص بك
API_TOKEN = '8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM'
bot = telebot.TeleBot(API_TOKEN)

# 🛠️ إعدادات القيادة العليا والتحكم (تم التحديث للآيدي الخاص بك بنجاح)
ADMIN_CHAT_ID = '1609075265' 
WITHDRAW_OPEN = False       

# 🌐 العناوين الرسمية الخاصة بك الثابتة بالملي للدفع داخل الميني أب
ADMIN_WALLETS = {
    'BEP20': '0x0aae3b8ed565178c5224296429310959536a80b6',
    'TRC20': 'TFF2ehjWuWTA1k3rrJVbaz2tbUhAZDobni',
    'TON': 'UQAO-l2K9qQtbHzLGiWyyGRtsaGBh0t82qHaa2GDMqq49Lp8'
}

# 💾 قاعدة بيانات السيرفر المركزية المؤقتة
users_db = {}
clans_db = []

def init_user(user_id, username="محارب أسطوري"):
    if user_id not in users_db:
        users_db[user_id] = {
            'username': username,
            'gold': 1000,
            'gems': 500,
            'castle_level': 1,
            'army_size': 20,
            'clan': 'بدون عشيرة',
            'invited_by': None,
            'referrals_count': 0
        }

# 🔗 سحب رابط ريلواي تلقائياً للميني أب
PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
WEBAPP_URL = f"https://{PUBLIC_DOMAIN}" if PUBLIC_DOMAIN else "https://example.com"


# 🎮 تابع بناء وتحديث لوحة تحكم الأدمن بالأزرار التفاعلية
def send_admin_panel(message, edit=False):
    status_str = "🔓 مفتوح ومتاح" if WITHDRAW_OPEN else "🔒 مغلق ومؤمن"
    text = f"🛠️ **مرحباً بك في لوحة تحكم الإدارة العليا (@II_2P)**\n\nوضع السحب الحالي: **{status_str}**\n\nتحكم بالخزائن أو ابحث عن اللاعبين لتأكيد شحنهم يدوياً بدون أوامر:"
    
    markup = types.InlineKeyboardMarkup()
    btn_on = types.InlineKeyboardButton("🔓 فتح السحب", callback_data="adm_wdon")
    btn_off = types.InlineKeyboardButton("🔒 قفل السحب", callback_data="adm_wdoff")
    btn_search = types.InlineKeyboardButton("🔎 بحث عن آيدي لاعب", callback_data="adm_search")
    btn_back = types.InlineKeyboardButton("↩️ القائمة الرئيسية", callback_data="adm_main")
    
    markup.row(btn_on, btn_off)
    markup.row(btn_search)
    markup.row(btn_back)
    
    if edit:
        try:
            bot.edit_message_text(text, chat_id=ADMIN_CHAT_ID, message_id=message.message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception: pass
    else:
        bot.send_message(ADMIN_CHAT_ID, text, reply_markup=markup, parse_mode="Markdown")


# ⚔️ أمر الدخول والترحيب باللاعبين والأدمن
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    is_new_user = user_id not in users_db
    init_user(user_id, user_name)
    
    command_args = message.text.split()
    if len(command_args) > 1 and is_new_user:
        referrer_id = command_args[1]
        if referrer_id != user_id and referrer_id in users_db:
            if users_db[user_id]['invited_by'] is None:
                users_db[user_id]['invited_by'] = referrer_id
                users_db[referrer_id]['referrals_count'] += 1
                users_db[referrer_id]['gems'] += 200
                try: bot.send_message(referrer_id, f"🎉 انضم محارب جديد عن طريقك! حصلت على +200 جوهرة حربية! 💎")
                except Exception: pass

    if user_id == ADMIN_CHAT_ID:
        welcome_text = f"🔥 مرحبًا بك يا قائدنا الأعلى {user_name}!\n\nيمكنك فتح اللعبة لتجربتها، أو الدخول مباشرة للوحة التحكم بالأزرار لإدارة السحب والبحث عن آيادي اللاعبين لتأكيد شحن الجواهر 👇"
        markup = types.InlineKeyboardMarkup()
        btn_webapp = types.InlineKeyboardButton("🎮 دخول اللعبة (Mini App)", web_app=types.WebAppInfo(url=WEBAPP_URL))
        btn_admin = types.InlineKeyboardButton("🛠️ لوحة تحكم الإدارة", callback_data="adm_panel")
        markup.add(btn_webapp)
        markup.add(btn_admin)
    else:
        welcome_text = f"🔥 مرحبًا بك في ساحة معارك APEX WARLORDS أيها القائد {user_name}!\n\nاضغط على الزر بالأسفل لفتح تطبيق الميني أب مباشرة، وبناء إمبراطوريتك وشحن الجواهر من المتجر الداخلي! ⚔️💎"
        markup = types.InlineKeyboardMarkup()
        btn_webapp = types.InlineKeyboardButton("🎮 افتح الإمبراطورية (Mini App)", web_app=types.WebAppInfo(url=WEBAPP_URL))
        markup.add(btn_webapp)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# 🔎 معالج البحث عن آيدي لاعب خطوة بخطوة (بدون أوامر نصية)
def process_user_search(message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return
    
    target_id = message.text.strip()
    if target_id in users_db:
        user = users_db[target_id]
        info_text = (
            f"👤 **بيانات اللاعب المستهدف:**\n\n"
            f"🆔 الآيدي: `{target_id}`\n"
            f"👤 الاسم: {user['username']}\n"
            f"🪙 الذهب: {user['gold']}\n"
            f"💎 الجواهر الحالية: {user['gems']}\n"
            f"🏰 مستوى القلعة: {user['castle_level']}\n\n"
            f"👇 يمكنك شحن جواهر فورية للاعب مباشرة من هنا:"
        )
        markup = types.InlineKeyboardMarkup()
        btn_100 = types.InlineKeyboardButton("➕ شحن 100 💎", callback_data=f"ap_100_{target_id}")
        btn_500 = types.InlineKeyboardButton("➕ شحن 500 💎", callback_data=f"ap_500_{target_id}")
        btn_1000 = types.InlineKeyboardButton("➕ شحن 1000 💎", callback_data=f"ap_1000_{target_id}")
        btn_5000 = types.InlineKeyboardButton("➕ شحن 5000 💎", callback_data=f"ap_5000_{target_id}")
        btn_back = types.InlineKeyboardButton("↩️ العودة للوحة التحكم", callback_data="adm_panel")
        
        markup.row(btn_100, btn_500)
        markup.row(btn_1000, btn_5000)
        markup.row(btn_back)
        
        bot.send_message(ADMIN_CHAT_ID, info_text, reply_markup=markup, parse_mode="Markdown")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 المحاولة مجدداً", callback_data="adm_search"))
        markup.add(types.InlineKeyboardButton("↩️ إلغاء والعودة", callback_data="adm_panel"))
        bot.send_message(ADMIN_CHAT_ID, "❌ عذراً، هذا الآيدي غير مسجل في قاعدة بيانات السيرفر حالياً!", reply_markup=markup)


# ⚖️ سنترال معالجة كل ضغطات الأزرار (شحن - سحب - لوحة تحكم أدمن)
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if str(call.from_user.id) != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "❌ غير مسموح لك بالولوغ لهذه الصلاحيات!")
        return
        
    data_parts = call.data.split("_")
    prefix = data_parts[0]
    
    if prefix == "adm":
        global WITHDRAW_OPEN
        action = data_parts[1]
        
        if action == "panel":
            send_admin_panel(call.message, edit=True)
        elif action == "wdon":
            WITHDRAW_OPEN = True
            bot.answer_callback_query(call.id, "🔓 تم تفعيل السحب")
            send_admin_panel(call.message, edit=True)
        elif action == "wdoff":
            WITHDRAW_OPEN = False
            bot.answer_callback_query(call.id, "🔒 تم قفل السحب")
            send_admin_panel(call.message, edit=True)
        elif action == "search":
            bot.answer_callback_query(call.id, "🔍 أرسل الآيدي الآن")
            msg = bot.send_message(ADMIN_CHAT_ID, "📥 **من فضلك أرسل آيدي التليجرام الخاص باللاعب المراد البحث عنه وتأكيد شحنه:**")
            bot.register_next_step_handler(msg, process_user_search)
        elif action == "main":
            markup = types.InlineKeyboardMarkup()
            btn_webapp = types.InlineKeyboardButton("🎮 دخول اللعبة (Mini App)", web_app=types.WebAppInfo(url=WEBAPP_URL))
            btn_admin = types.InlineKeyboardButton("🛠️ لوحة تحكم الإدارة", callback_data="adm_panel")
            markup.add(btn_webapp)
            markup.add(btn_admin)
            bot.edit_message_text(f"🔥 مرحبًا بك يا قائدنا الأعلى وسيد المعارك!\n\nيمكنك فتح اللعبة لتجربتها، أو الدخول مباشرة للوحة التحكم بالأزرار لإدارة وضعيات الشحن والسحب بالكامل 👇", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id, reply_markup=markup)

    elif prefix == "ap":
        action = data_parts[1]
        target_user_id = data_parts[2]
        init_user(target_user_id)
        
        if action == "rej":
            bot.edit_message_caption("❌ تم رفض طلب الشحن وإخطار اللاعب تلقائياً.", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
            try: bot.send_message(target_user_id, "❌ نأسف أيها القائد، تم رفض إيصال الشحن الخاص بك من قبل الإدارة بعد مراجعة الحسابات.")
            except Exception: pass
        else:
            gems_to_add = int(action)
            users_db[target_user_id]['gems'] += gems_to_add
            
            try:
                bot.edit_message_caption(f"✅ تم تأكيد التحويل وضخ +{gems_to_add} 💎 في حساب اللاعب بنجاح!", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
            except Exception:
                try: bot.edit_message_text(f"✅ تم تأكيد التحويل وضخ +{gems_to_add} 💎 في حساب اللاعب بنجاح!", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
                except Exception: pass
                
            try: bot.send_message(target_user_id, f"🎉 موافقة فورية من الإدارة! تم تأكيد إيصال الشحن الخاص بك بنجاح وإضافة +{gems_to_add} 💎 لحسابك.")
            except Exception: pass

    elif prefix == "wd":
        action = data_parts[1]
        target_user_id = data_parts[2]
        gold_amount = int(data_parts[3]) if len(data_parts) > 3 else 0
        init_user(target_user_id)
        
        if action == "approve":
            if users_db[target_user_id]['gold'] >= gold_amount:
                users_db[target_user_id]['gold'] -= gold_amount
                bot.edit_message_text(f"✅ تم تأكيد إرسال الكريبتو بنجاح وخصم {gold_amount} 🪙 من اللاعب!", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
                try: bot.send_message(target_user_id, f"💰 مبروك أيها القائد العظيم! وافقت الإدارة على طلب السحب الخاص بك وتم إرسال العملات الرقمية لمحفظتك وخصم {gold_amount} 🪙.")
                except Exception: pass
            else:
                bot.edit_message_text("❌ فشل الخصم: رصيد الذهب الحالي للاعب غير كافي للسحب!", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
        elif action == "reject":
            bot.edit_message_text("❌ تم رفض طلب سحب المكافأة وإخطار المستخدم بالرفض الصارم.", chat_id=ADMIN_CHAT_ID, message_id=call.message.message_id)
            try: bot.send_message(target_user_id, "❌ نأسف، تم رفض طلب سحب المكافآت الخاص بك من قبل الإدارة لمخالفة القوانين العسكرية.")
            except Exception: pass


# 🎨 واجهة اللعبة الاحترافية (HTML / CSS / JavaScript)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Warlords</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            background-color: #0f0f12; color: #ffffff; font-family: 'Segoe UI', sans-serif;
            margin: 0; padding: 15px; text-align: center; direction: rtl; -webkit-user-select: none;
        }
        .header h1 { color: #ff9f43; font-size: 24px; margin: 5px 0; text-shadow: 0 0 10px rgba(255,159,67,0.4); }
        .welcome-msg { color: #a4b0be; font-size: 13px; margin-bottom: 2px; }
        .tg-id-badge { display: inline-block; background: #2f3542; color: #00d2d3; font-size: 11px; padding: 3px 8px; border-radius: 4px; margin-bottom: 12px; font-family: monospace; }
        
        .season-banner { background: linear-gradient(90deg, #ff4757, #b33939); color: white; font-size: 12px; font-weight: bold; padding: 6px; border-radius: 6px; margin-bottom: 15px; border: 1px solid #ff6b81; box-shadow: 0 0 8px rgba(255,71,87,0.3); }
        
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
        .stat-card { background: #18181c; border: 1px solid #2f3542; border-radius: 10px; padding: 10px; }
        .stat-label { font-size: 12px; color: #747d8c; display: block; }
        .stat-val { font-size: 16px; font-weight: bold; color: #ff9f43; }
        .gems-val { color: #00d2d3 !important; }
        
        .store-title { font-size: 16px; font-weight: bold; color: #00d2d3; text-align: right; margin: 20px 0 10px 0; display: block; border-right: 3px solid #00d2d3; padding-right: 8px;}
        .store-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        .shop-card { background: linear-gradient(135deg, #1c1c24, #121217); border: 1px solid #00d2d340; border-radius: 12px; padding: 12px; position: relative; cursor: pointer; }
        .shop-card:active { transform: scale(0.96); border-color: #00d2d3; }
        .shop-gems { font-size: 17px; font-weight: bold; color: #fff; display: block; }
        .shop-price { font-size: 12px; color: #2ed573; font-weight: bold; display: block; margin-top: 4px; }
        
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 100; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; }
        .modal-content { background: #16161e; border: 2px solid #00d2d3; border-radius: 15px; width: 100%; max-width: 400px; padding: 20px; text-align: right; box-sizing: border-box; }
        .modal-h { font-size: 18px; color: #ff9f43; margin-top: 0; display: block; text-align: center; font-weight: bold; margin-bottom: 15px;}
        .wallet-box { background: #0f0f13; border: 1px dashed #747d8c; border-radius: 8px; padding: 10px; font-size: 11px; color: #fff; font-family: monospace; word-break: break-all; margin-bottom: 10px; text-align: center; }
        
        .selector-input { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #2f3542; background: #18181c; color: white; font-size: 13px; margin-bottom: 12px; font-weight: bold; }
        .web3-section { background: #112233; border: 1px solid #00d2d3; border-radius: 10px; padding: 12px; margin-bottom: 15px; text-align: right; }
        .web3-title { font-size: 14px; font-weight: bold; color: #00d2d3; margin-bottom: 5px; display: block;}
        .web3-input { width: 93%; padding: 8px; border-radius: 5px; border: 1px solid #2f3542; background: #18181c; color: white; font-size: 12px; margin-bottom: 5px; text-align: left; }
        .log-box { background: #16161a; border: 1px solid #2ed573; border-radius: 8px; padding: 10px; font-size: 13px; color: #2ed573; min-height: 35px; margin-bottom: 15px; display: flex; align-items: center; justify-content: center;}
        .btn { background: linear-gradient(90deg, #ff9f43, #ff6b81); color: white; border: none; border-radius: 8px; padding: 14px; width: 100%; font-size: 15px; font-weight: bold; margin-bottom: 8px; cursor: pointer; }
        .btn-secondary { background: #2f3542; border: 1px solid #57606f; font-size: 13px; padding: 10px; }
        .btn-web3 { background: #00d2d3; color: #121214; padding: 8px 15px; border-radius: 5px; font-size: 12px; font-weight: bold; border: none; cursor: pointer; }
    </style>
</head>
<body>

    <div class="header">
        <h1>⚔️ APEX WARLORDS ⚔️</h1>
        <div class="welcome-msg" id="username">أيها القائد الباسل</div>
        <div class="tg-id-badge">Telegram ID: <span id="player-tg-id">000000000</span></div>
    </div>

    <div class="season-banner">⏳ تنبيه: ينتهي السيزون الحالي ويتم توزيع المكافآت يوم 12/7/2026!</div>

    <div class="stats-grid">
        <div class="stat-card"><span class="stat-label">🪙 الذهب بالخزينة</span><span class="stat-val" id="gold">0</span></div>
        <div class="stat-card"><span class="stat-label">💎 الجواهر الممتازة</span><span class="stat-val gems-val" id="gems">0</span></div>
        <div class="stat-card"><span class="stat-label">🏰 مستوى القلعة</span><span class="stat-val" id="castle">1</span></div>
        <div class="stat-card"><span class="stat-label">🪖 حجم الجيش</span><span class="stat-val" id="army">0</span></div>
    </div>

    <div class="log-box" id="log-box">🛡️ القوات مستعدة وفي انتظار الأوامر العسكرية العليا!</div>

    <button class="btn" onclick="performAction('raid')">💣 شن غارة هجومية عسكرية ⚔️</button>
    <button class="btn btn-secondary" onclick="performAction('train')">🪖 تدريب كتيبة عساكر جديدة (200 🪙)</button>
    
    <button class="btn" style="background: linear-gradient(90deg, #2ed573, #1e3799);" onclick="checkAndOpenWithdrawModal()">💰 سحب المكافآت والأرباح</button>

    <span class="store-title">💎 متجر شحن الجواهر الفوري</span>
    <div class="store-grid">
        <div class="shop-card" onclick="openDepositModal(100, '$0.30')"><span class="shop-gems">💎 100 جوهرة</span><span class="shop-price">$0.30</span></div>
        <div class="shop-card" onclick="openDepositModal(500, '$1.50')"><span class="shop-gems">💎 500 جوهرة</span><span class="shop-price">$1.50</span></div>
        <div class="shop-card" onclick="openDepositModal(1000, '$3.00')"><span class="shop-gems">💎 1000 جوهرة</span><span class="shop-price">$3.00</span></div>
        <div class="shop-card" onclick="openDepositModal(5000, '$15.00')"><span class="shop-gems">💎 5000 جوهرة</span><span class="shop-price">$15.00</span></div>
        <div class="shop-card" style="grid-column: span 2;" onclick="openDepositModal(10000, '$30.00')"><span class="shop-gems">💎 10000 جوهرة أسطورية</span><span class="shop-price">$30.00</span></div>
    </div>

    <div class="web3-section">
        <span class="web3-title">🛡️ حلف العشيرة الحالي: <span id="clan-status" style="color:white;">بدون عشيرة</span></span>
        <input type="text" id="clan-name-input" class="web3-input" placeholder="اكتب اسم العشيرة الجديدة هنا...">
        <button class="btn-web3" style="background:#ff9f43;" onclick="createClan()">تأسيس عشيرة حربية (5000 💎)</button>
    </div>
    
    <button class="btn btn-secondary" style="background: #0c0c0e; border-color: #00d2d3; color: #00d2d3;" onclick="showInviteLink()">🔗 نسخ رابط جلب الحلفاء (+200 💎)</button>


    <div class="modal-overlay" id="deposit-modal">
        <div class="modal-content">
            <span class="modal-h" id="modal-package-title">شحن الجواهر</span>
            
            <label style="font-size:12px; color:#a4b0be; display:block; margin-bottom:5px;">👤 آيدي التليجرام الخاص بك (للتأكيد):</label>
            <input type="text" id="deposit-user-id" class="web3-input" style="width:94%; text-align:center; font-weight:bold; color:#00d2d3; margin-bottom:12px;" placeholder="آيدي حسابك">

            <label style="font-size:12px; color:#a4b0be; display:block; margin-bottom:5px;">اختر شبكة الدفع المناسبة لك:</label>
            <select id="deposit-network" class="selector-input" onchange="updateDepositWalletDisplay()">
                <option value="BEP20">Binance Smart Chain (BEP20)</option>
                <option value="TRC20">USDT / TRON (TRC20)</option>
                <option value="TON">TON / Gram Network</option>
            </select>

            <span style="font-size:12px; color:#a4b0be; display:block; margin-bottom:5px;">عنوان محفظة الإدارة للتحويل:</span>
            <div class="wallet-box" id="admin-wallet-txt">تجري القراءة...</div>
            <button class="btn-web3" style="width:100%; background:#ff9f43; margin-bottom:15px;" onclick="copyAdminWallet()">📋 نسخ العنوان المختار</button>
            
            <hr style="border:0; border-top:1px solid #2f3542; margin-bottom:12px;">
            <span style="font-size:12px; color:#2ed573; font-weight:bold; display:block; margin-bottom:5px;">📥 ارفع لقطة الشاشة للإيصال (Screenshot):</span>
            <input type="file" id="screenshot-file" accept="image/*" style="width:100%; background:#18181c; padding:5px; border-radius:5px; color:white;">
            
            <button class="btn" style="margin-top:15px; background:linear-gradient(90deg, #2ed573, #1e3799);" id="btn-submit-pay" onclick="submitPaymentToServer()">🚀 إرسال الإيصال للمراجعة</button>
            <button class="btn btn-secondary" style="margin-top:5px; width:100%;" onclick="closeDepositModal()">إلغاء</button>
        </div>
    </div>


    <div class="modal-overlay" id="withdraw-modal">
        <div class="modal-content">
            <span class="modal-h" style="color:#2ed573;">طلب سحب المكافآت</span>
            
            <label style="font-size:12px; color:#a4b0be; display:block; margin-bottom:4px;">حدد شبكة السحب:</label>
            <select id="withdraw-network" class="selector-input">
                <option value="BEP20">BEP20 Wallet</option>
                <option value="TRC20">TRC20 Wallet</option>
                <option value="TON">TON / Gram Wallet</option>
            </select>
            
            <label style="font-size:12px; color:#a4b0be; display:block; margin-bottom:4px;">كمية الذهب المراد سحبها:</label>
            <input type="number" id="withdraw-amount" class="web3-input" style="width:94%; text-align:center;" placeholder="مثال: 5000" min="1000">
            
            <label style="font-size:12px; color:#a4b0be; display:block; margin-bottom:4px; margin-top:8px;">عنوان محفظتك أنت لاستلام الأموال:</label>
            <input type="text" id="user-wallet-address" class="web3-input" style="width:94%; text-align:left; font-family:monospace;" placeholder="ألصق عنوانك هنا بدقة...">
            
            <button class="btn" style="margin-top:15px; background:linear-gradient(90deg, #ff9f43, #ff4757);" id="btn-submit-wd" onclick="submitWithdrawToServer()">🚀 إرسال طلب السحب للقيادة</button>
            <button class="btn btn-secondary" style="margin-top:5px; width:100%;" onclick="closeWithdrawModal()">إغلاق</button>
        </div>
    </div>


    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        let userId = "test_user";
        let username = "القائد";
        let selectedGems = 0;
        let cachedWallets = {};

        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            userId = tg.initDataUnsafe.user.id.toString();
            username = tg.initDataUnsafe.user.first_name;
            document.getElementById('username').innerText = "القائد: " + username;
            document.getElementById('player-tg-id').innerText = userId;
        }

        function loadPlayerData() {
            fetch(`/api/get_user?user_id=${userId}&username=${encodeURIComponent(username)}`)
                .then(res => res.json())
                .then(data => updateUI(data));
        }

        function updateUI(data) {
            document.getElementById('gold').innerText = data.gold;
            document.getElementById('gems').innerText = data.gems;
            document.getElementById('castle').innerText = data.castle_level;
            document.getElementById('army').innerText = data.army_size;
            document.getElementById('clan-status').innerText = data.clan;
        }

        function showLog(text, isSuccess) {
            const log = document.getElementById('log-box');
            log.innerText = text;
            log.style.borderColor = isSuccess ? "#2ed573" : "#ff4757";
            log.style.color = isSuccess ? "#2ed573" : "#ff6b81";
        }

        function openDepositModal(gems, price) {
            selectedGems = gems;
            document.getElementById('modal-package-title').innerText = `شحن حزمة ${gems} جوهرة (${price})`;
            document.getElementById('deposit-user-id').value = userId; 
            
            fetch('/api/get_admin_config')
                .then(res => res.json())
                .then(data => {
                    cachedWallets = data.wallets;
                    updateDepositWalletDisplay();
                    document.getElementById('deposit-modal').style.display = 'flex';
                });
        }

        function updateDepositWalletDisplay() {
            const net = document.getElementById('deposit-network').value;
            if(cachedWallets[net]) {
                document.getElementById('admin-wallet-txt').innerText = cachedWallets[net];
            }
        }

        function closeDepositModal() {
            document.getElementById('deposit-modal').style.display = 'none';
        }

        function copyAdminWallet() {
            const walletStr = document.getElementById('admin-wallet-txt').innerText;
            navigator.clipboard.writeText(walletStr);
            alert("📋 تم نسخ العنوان المختار إلى حافظتك بنجاح!");
        }

        function submitPaymentToServer() {
            const fileInput = document.getElementById('screenshot-file');
            const net = document.getElementById('deposit-network').value;
            const inputId = document.getElementById('deposit-user-id').value.trim();
            
            if(fileInput.files.length === 0) { alert("❌ يرجى اختيار صورة إيصال التحويل أولاً!"); return; }
            if(!inputId) { alert("❌ يرجى ملء خانة آيدي التليجرام الخاص بك!"); return; }
            
            const btnSubmit = document.getElementById('btn-submit-pay');
            btnSubmit.innerText = "⏳ جاري الإرسال...";
            btnSubmit.disabled = true;

            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('custom_telegram_id', inputId);
            formData.append('username', username);
            formData.append('gems_amount', selectedGems);
            formData.append('network', net);
            formData.append('screenshot', fileInput.files[0]);

            fetch('/api/submit_deposit', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                btnSubmit.innerText = "🚀 إرسال الإيصال للمراجعة";
                btnSubmit.disabled = false;
                closeDepositModal();
                if(data.success) {
                    showLog(`⏳ طلب شحن ${selectedGems} 💎 قيد المراجعة الآن!`, true);
                    alert("انتظر قيد المراجعة لا تقلق");
                } else { alert("❌ خطأ: " + data.error); }
            });
        }

        function checkAndOpenWithdrawModal() {
            fetch('/api/check_withdraw_status')
                .then(res => res.json())
                .then(data => {
                    if(!data.open) {
                        alert("⚠️ نأسف أيها القائد! السحب مغلق حالياً بطلب من القيادة، سيتم فتحه فوراً عند صدور التعليمات.");
                    } else {
                        document.getElementById('withdraw-modal').style.display = 'flex';
                    }
                });
        }

        function closeWithdrawModal() {
            document.getElementById('withdraw-modal').style.display = 'none';
        }

        function submitWithdrawToServer() {
            const amount = parseInt(document.getElementById('withdraw-amount').value);
            const userWallet = document.getElementById('user-wallet-address').value.trim();
            const net = document.getElementById('withdraw-network').value;
            const currentGold = parseInt(document.getElementById('gold').innerText);
            
            if(!amount || amount <= 0) { alert("❌ يرجى إدخال كمية ذهب صحيحة!"); return; }
            if(amount > currentGold) { alert("❌ رصيد الذهب الحالي لديك لا يكفي لإتمام هذا السحب!"); return; }
            if(!userWallet) { alert("❌ يرجى وضع عنوان محفظتك لاستلام الموارد عليها!"); return; }
            
            const btnSubmit = document.getElementById('btn-submit-wd');
            btnSubmit.innerText = "⏳ جاري معالجة الطلب...";
            btnSubmit.disabled = true;

            fetch('/api/submit_withdraw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, username: username, amount: amount, network: net, wallet: userWallet })
            })
            .then(res => res.json())
            .then(data => {
                btnSubmit.innerText = "🚀 إرسال طلب السحب للقيادة";
                btnSubmit.disabled = false;
                closeWithdrawModal();
                if(data.success) {
                    showLog(`💰 تم تقديم طلب سحب لـ ${amount} ذهبة بنجاح، وهو قيد المراجعة الفورية!`, true);
                    alert("⏳ تم تقديم طلبك بنجاح! سينظر فيه المشرفون ويتم إرسال العملات لمحفظتك قريباً.");
                } else { alert("❌ خطأ: " + data.error); }
            });
        }

        function performAction(actionType) {
            fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, action: actionType })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) { showLog(data.error, false); } 
                else { showLog(data.msg, true); updateUI(data.stats); }
            });
        }

        function createClan() {
            const clanName = document.getElementById('clan-name-input').value.trim();
            if(!clanName) { alert("اكتب اسم العشيرة أولاً!"); return; }
            fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, action: 'create_clan', clan_name: clanName })
            })
            .then(res => res.json())
            .then(data => {
                if(data.error) { alert(data.error); } 
                else { updateUI(data.stats); alert(data.msg); }
            });
        }

        function showInviteLink() {
            navigator.clipboard.writeText(`https://t.me/Apex_Warlords_Bot?start=${userId}`);
            alert("🔗 تم نسخ رابط الإحالة الحربي الخاص بك! (+200 💎)");
        }

        loadPlayerData();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

@app.route('/api/get_admin_config', methods=['GET'])
def get_admin_config():
    return jsonify({'wallets': ADMIN_WALLETS})

@app.route('/api/check_withdraw_status', methods=['GET'])
def check_withdraw_status():
    return jsonify({'open': WITHDRAW_OPEN})

@app.route('/api/submit_deposit', methods=['POST'])
def submit_deposit():
    user_id = request.form.get('user_id')
    custom_tg_id = request.form.get('custom_telegram_id', user_id)
    user_name = request.form.get('username', 'محارب')
    gems_amount = request.form.get('gems_amount', '0')
    network = request.form.get('network', 'غير محددة')
    
    if 'screenshot' not in request.files:
        return jsonify({'success': False, 'error': 'الملف مفقود'}), 400
    file = request.files['screenshot']
    
    try:
        admin_markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton(f"✅ موافقة وشحن (+{gems_amount} 💎)", callback_data=f"ap_{gems_amount}_{user_id}")
        btn_reject = types.InlineKeyboardButton("❌ رفض الشحن", callback_data=f"ap_rej_{user_id}")
        admin_markup.add(btn_approve)
        admin_markup.add(btn_reject)
        
        bot.send_photo(
            ADMIN_CHAT_ID,
            file.stream,
            caption=f"📥 **إيصال شحن جديد تم رفعه من الميني أب!**\n\n👤 اللاعب: {user_name}\n🆔 آيدي التليجرام المدخل: `{custom_tg_id}`\n💎 **الكمية المطلوبة للشحن: {gems_amount} جوهرة**\n🌐 الشبكة المستخدمة: `{network}`\n\nتأكد من المعاملة في محفظتك ثم اضغط للاعتماد الفوري 👇",
            reply_markup=admin_markup,
            parse_mode="Markdown"
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/submit_withdraw', methods=['POST'])
def submit_withdraw():
    if not WITHDRAW_OPEN:
        return jsonify({'success': False, 'error': 'السحب مغلق حالياً بطلب من الإدارة!'})
        
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('username', 'محارب')
    amount = data.get('amount', 0)
    network = data.get('network')
    user_wallet = data.get('wallet')
    
    init_user(user_id)
    if users_db[user_id]['gold'] < amount:
        return jsonify({'success': False, 'error': 'رصيد الذهب غير كافي!'})
        
    try:
        admin_markup = types.InlineKeyboardMarkup()
        btn_ok = types.InlineKeyboardButton("✅ تم التحويل (تأكيد الخصم)", callback_data=f"wd_approve_{user_id}_{amount}")
        btn_no = types.InlineKeyboardButton("❌ رفض طلب السحب", callback_data=f"wd_reject_{user_id}")
        admin_markup.add(btn_ok)
        admin_markup.add(btn_no)
        
        bot.send_message(
            ADMIN_CHAT_ID,
            f"💰 **طلب سحب مكافأة معلق!**\n\n👤 اللاعب: {user_name}\n🆔 الآيدي: `{user_id}`\n🪙 الكمية المطلوبة: *{amount} ذهبة*\n🌐 شبكة السحب: `{network}`\n💳 عنوان محفظة اللاعب:\n`{user_wallet}`\n\n⚠️ قم بنسخ محفظة اللاعب وحول له، ثم اضغط على زر التأكيد ليتم الخصم تلقائياً!",
            reply_markup=admin_markup,
            parse_mode="Markdown"
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    username = request.args.get('username', 'محارب أسطوري')
    init_user(user_id, username)
    return jsonify(users_db[user_id])

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')
    init_user(user_id)
    user = users_db[user_id]
    
    if action == 'train':
        if user['gold'] >= 200:
            user['gold'] -= 200
            user['army_size'] += 15
            return jsonify({'msg': '🪖 تم تدريب فرقة عساكر بنجاح! وانضم +15 جندي لصفوفك.', 'stats': user})
        else:
            return jsonify({'error': '❌ الذهب غير كافي لتغطية تكاليف التدريب العسكري (200 🪙).'})
            
    elif action == 'raid':
        if user['army_size'] < 10:
            return jsonify({'error': '⚠️ جيشك ضعيف جداً! درب عساكر أولاً قبل شن الغارة.'})
        if random.choices([True, False], weights=[65, 35])[0]:
            looted = random.randint(300, 700)
            lost = random.randint(2, 6)
            user['gold'] += looted
            user['army_size'] = max(0, user['army_size'] - lost)
            return jsonify({'msg': f'🔥 انتصار ساحق! غنمت +{looted} ذهبة 🪙.', 'stats': user})
        else:
            lost_gold = random.randint(150, 300)
            lost_troops = random.randint(6, 12)
            user['gold'] = max(0, user['gold'] - lost_gold)
            user['army_size'] = max(0, user['army_size'] - lost_troops)
            return jsonify({'msg': f'💀 وقع جيشك في كمين الأعداء وخسرت موارد!', 'stats': user})

    elif action == 'create_clan':
        clan_name = data.get('clan_name', '').strip()
        if user['gems'] < 5000: return jsonify({'error': '❌ تحتاج إلى 5000 💎 لتأسيس عشيرة.'})
        if clan_name in clans_db: return jsonify({'error': '❌ اسم هذه العشيرة مأخوذ!'})
        user['gems'] -= 5000
        user['clan'] = clan_name
        clans_db.append(clan_name)
        return jsonify({'msg': f'🛡️ ألف مبروك! تم تأسيس عشيرة [{clan_name}] بنجاح!', 'stats': user})

    return jsonify({'error': 'عملية غير معروفة'})

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

