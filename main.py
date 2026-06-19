import os
import telebot
from telebot import types

# ريلواي هيقرأ التوكن تلقائياً من المتغيرات السرية (Variables) باسم BOT_TOKEN
API_TOKEN = os.environ.get('8895527275:AAEh3hBBR6IQGc9APTcdK8RZqPaZNXvCfnM')

bot = telebot.TeleBot(API_TOKEN)

# رسالة الترحيب الحماسية المخصصة باسم اللعبة الجديد
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name 
    
    welcome_text = f"""🔥 Welcome to the arena, Mythic Warrior {user_name}! ✊

Prepare yourself for the ultimate challenge in the realm of APEX WARLORDS! ⚔️

Your legend starts today:
🏰 Build an unbreakable empire
💣 Expand your territory & rule the map
👥 Form elite clans & smash your rivals in epic wars!

💰 Huge prize pools are waiting! Active players get paid at the end of every short season. Don't miss out!

May victory and endless glory be yours, brave fighter! 🛡️✨"""

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_start = types.InlineKeyboardButton("🎮 Start Playing Now", callback_data="start_game")
    
    # 📢 هنا تم إضافة رابط قناتك الرسمي والمظبوط
    btn_channel = types.InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/Apex_Warlords")
    
    btn_invite = types.InlineKeyboardButton("👥 Invite Friends (Earn Bonus)", callback_data="invite")
    
    markup.add(btn_start, btn_channel, btn_invite)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

if __name__ == "__main__":
    print("البوت انطلق في سيرفرات ريلواي... 🔥")
    bot.infinity_polling()

