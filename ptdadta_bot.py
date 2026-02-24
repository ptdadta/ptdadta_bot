import telebot
from telebot import types
import random
import json
import os

TOKEN = "7759858144:AAHl7P5FBuiBDKwIj0nzcBox6eewms7gqVM"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"

def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    try:
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения: {e}")

users = load_users()

# Вопросы
QUESTIONS = [
    {"q": "2 + 2 = ?", "options": ["3", "4", "5"], "ans": 1},
    {"q": "Столица России?", "options": ["Москва", "Питер", "Новосибирск"], "ans": 0},
    {"q": "Сколько дней в неделе?", "options": ["5", "6", "7"], "ans": 2},
    {"q": "Кто сказал 'ПТДАДТА ВЕЧНА'?", "options": ["Игорь", "Ильяс", "Олег"], "ans": 0},
    {"q": "Что лучше сбивать?", "options": ["Машины", "Бабушек", "Автокраны"], "ans": 2},
    {"q": "Кто такой Ильяс?", "options": ["Друг", "Враг", "Легенда"], "ans": 2},
]

# Предметы
ITEMS = {
    "легковушка": ["жигули", "бэха", "приора"],
    "животные": ["заяц", "ёж", "лось"],
    "бабки": ["бабка с авоськой", "бабка-сплетница"],
    "деды": ["дед с яйцом", "дед с клюшкой"],
    "менты": ["мент", "дпс"],
    "мутанты": ["радиоактивный ёж", "лось с рентгеном"]
}

# Фразы
PHRASES = {
    "легковушка": "💥 МАШИНА В ХЛАМ!",
    "животные": "🦔 ЗВЕРЬ ГОТОВ!",
    "бабки": "👵 БАБКА В ПОЛЁТЕ!",
    "деды": "🧓 ДЕД КУВЫРКОМ!",
    "менты": "👮 МЕНТ В КЮВЕТЕ!",
    "мутанты": "👽 МУТАНТ УНИЧТОЖЕН!"
}

# Кнопки меню
def menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("💥 СБИТЬ"),
        types.KeyboardButton("😇 ПОЩАДИТЬ"),
        types.KeyboardButton("⚔️ БОЙНЯ"),
        types.KeyboardButton("📊 СТАТИСТИКА"),
        types.KeyboardButton("🏆 ТОП"),
        types.KeyboardButton("🎯 АЧИВКИ")
    )
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    name = message.from_user.first_name
    
    if uid not in users:
        users[uid] = {
            "name": name,
            "points": 0,
            "lives": 5,
            "kills": 0,
            "подрезы": 0,
            "items": {}
        }
        save_users(users)
        bot.reply_to(message, f"🎉 Добро пожаловать, {name}!\nПТДАДТА ВЕЧНА!")
    else:
        bot.reply_to(message, f"С возвращением, {name}!")
    
    new_encounter(uid)

def new_encounter(uid):
    cat = random.choice(list(ITEMS.keys()))
    item = random.choice(ITEMS[cat])
    users[uid]["current"] = {"cat": cat, "item": item}
    save_users(users)
    bot.send_message(uid, f"🚗 Ты видишь: {item} ({cat})", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda m: True)
def handler(message):
    uid = str(message.chat.id)
    text = message.text
    
    if uid not in users:
        bot.send_message(uid, "Напиши /start")
        return
    
    if text == "💥 СБИТЬ":
        if "current" not in users[uid]:
            new_encounter(uid)
            return
        
        q = random.choice(QUESTIONS)
        users[uid]["q"] = q
        
        kb = types.InlineKeyboardMarkup(row_width=1)
        for i, opt in enumerate(q["options"]):
            kb.add(types.InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
        
        bot.send_message(uid, f"❓ {q['q']}", reply_markup=kb)
    
    elif text == "😇 ПОЩАДИТЬ":
        users[uid]["points"] += 1
        save_users(users)
        bot.send_message(uid, "😇 Пощадил +1 очко")
        new_encounter(uid)
    
    elif text == "📊 СТАТИСТИКА":
        u = users[uid]
        bot.send_message(uid, 
            f"📊 Твоя статистика:\n"
            f"❤️ Жизни: {u['lives']}\n"
            f"📊 Очки: {u['points']}\n"
            f"🔪 Подрезы: {u['подрезы']}\n"
            f"💀 Убийств: {u['kills']}")
    
    elif text == "🏆 ТОП":
        top = sorted(users.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        msg = "🏆 ТОП-10:\n"
        for i, (uid, data) in enumerate(top, 1):
            msg += f"{i}. {data['name']} – {data['points']} очков\n"
        bot.send_message(uid, msg)
    
    elif text == "🎯 АЧИВКИ":
        bot.send_message(uid, "🛠 В разработке")
    
    elif text == "⚔️ БОЙНЯ":
        bot.send_message(uid, "🛠 В разработке")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = str(call.message.chat.id)
    data = call.data
    
    if data.startswith("ans_"):
        ans = int(data.split("_")[1])
        q = users[uid].get("q")
        
        if q and ans == q["ans"]:
            cat = users[uid]["current"]["cat"]
            users[uid]["points"] += 3
            users[uid]["подрезы"] += 1
            users[uid]["kills"] += 1
            bot.edit_message_text(
                chat_id=uid,
                message_id=call.message.message_id,
                text=f"✅ Верно!\n{PHRASES.get(cat, '💥 ЕБАШ!')}\n+3 очка, +1 подрез"
            )
        else:
            users[uid]["lives"] -= 2
            bot.edit_message_text(
                chat_id=uid,
                message_id=call.message.message_id,
                text=f"❌ Неверно!\n🧱 -2 жизни"
            )
        
        save_users(users)
        
        if users[uid]["lives"] <= 0:
            bot.send_message(uid, "💀 ТЫ УМЕР! /start")
            users[uid]["lives"] = 5
            users[uid]["points"] = 0
            users[uid]["kills"] = 0
            users[uid]["подрезы"] = 0
            save_users(users)
        else:
            new_encounter(uid)

if __name__ == "__main__":
    print("🚀 Это импортируемый модуль, запускай main.py")