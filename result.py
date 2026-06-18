import sqlite3
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8807570935:AAH2uliAMd52eurfEdqnDKiiyM0gzu0O8O4"
ADMIN_ID = 8135766988 
CHANNEL_ID = "@Profik_Studio"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ЦЕНЫ И ТОВАРЫ ---
PRODUCTS = {
    "br": {"name": "Копия Black Russia", "price": 150, "link": "https://github.com/IrvenDaro/BR_Full"},
    "matreshka": {"name": "Копия Matreshka RP", "price": 75, "link": "https://github.com/IrvenDaro/Matr_Full"},
    "grand": {"name": "Копия Grand Mobile", "price": 50, "link": "https://github.com/IrvenDaro/Grand_Full"},
    "hassle": {"name": "Копия Hassle Online", "price": 200, "link": "https://github.com/IrvenDaro/Hassle_Full"},
    "launcher": {"name": "Топовый Лаунчер", "price": 25, "link": "https://github.com/IrvenDaro/Launcher_Top"},
    "mod": {"name": "Топовый Мод", "price": 25, "link": "https://github.com/IrvenDaro/Mod_Top"},
    "instr": {"name": "VIP Инструкция", "price": 20, "link": "https://telegra.ph/Instrukciya-Profik-Studio"},
    "fill_mod": {"name": "Заливка мода на хост", "price": 25, "link": "https://github.com/IrvenDaro/Fill_Mod_Script"},
    "fill_db": {"name": "Заливка базы данных", "price": 15, "link": "https://github.com/IrvenDaro/Fill_DB_Script"}
}

# --- БАЗА ДАННЫХ ---
def db_query(sql, params=(), fetch=False):
    conn = sqlite3.connect("profik_studio.db")
    cur = conn.cursor()
    cur.execute(sql, params)
    res = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

def init_db():
    db_query('''CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, jenny_used INTEGER DEFAULT 0)''')

async def check_sub(user_id):
    try:
        m = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return m.status in ["member", "administrator", "creator"]
    except: return False

# --- КЛАВИАТУРЫ ---
def main_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    builder.row(types.InlineKeyboardButton(text="🚀 Создать проект", callback_data="cat_projects"))
    builder.row(types.InlineKeyboardButton(text="🛠 Заливка Мода / БД", callback_data="cat_services"))
    builder.row(types.InlineKeyboardButton(text="📱 Купить Лаунчер / Мод", callback_data="cat_shop"))
    builder.row(types.InlineKeyboardButton(text="📖 Инструкция (20 ⭐)", callback_data="buy_item:instr"))
    builder.row(types.InlineKeyboardButton(text="🎁 Бесплатная Дженни", callback_data="free_jenny"))
    if user_id == ADMIN_ID:
        builder.row(types.InlineKeyboardButton(text="👑 АДМИН ПАНЕЛЬ", callback_data="admin_menu"))
    return builder.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
@dp.callback_query(F.data == "to_main")
async def start(event):
    uid = event.from_user.id
    db_query("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))
    if not await check_sub(uid):
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        kb.row(types.InlineKeyboardButton(text="✅ Проверить подписку", callback_data="to_main"))
        msg = "⚠️ Чтобы пользоваться ботом, подпишись на наш канал @Profik_Studio!"
        if isinstance(event, types.Message): await event.answer(msg, reply_markup=kb.as_markup())
        else: await event.message.edit_text(msg, reply_markup=kb.as_markup())
    else:
        msg = "🚀 **Profik Studio** — Твой личный конструктор проектов!\nВсе покупки автоматизированы."
        if isinstance(event, types.Message): await event.answer(msg, reply_markup=main_kb(uid), parse_mode="Markdown")
        else: await event.message.edit_text(msg, reply_markup=main_kb(uid), parse_mode="Markdown")

@dp.callback_query(F.data == "profile")
async def profile(callback: types.CallbackQuery):
    u = db_query("SELECT balance FROM users WHERE id = ?", (callback.from_user.id,), fetch=True)[0]
    await callback.message.edit_text(f"👤 **Твой профиль**\n\n🆔 ID: `{callback.from_user.id}`\n💰 Баланс: {u[0]} ⭐\n\nПополнение баланса через владельца.", 
                                     reply_markup=main_kb(callback.from_user.id), parse_mode="Markdown")

@dp.callback_query(F.data == "cat_projects")
async def cat_projects(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for k in ["br", "matreshka", "grand", "hassle"]:
        builder.row(types.InlineKeyboardButton(text=f"{PRODUCTS[k]['name']} | {PRODUCTS[k]['price']}⭐", callback_data=f"buy_item:{k}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    await callback.message.edit_text("🔥 Выбери проект для создания:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "cat_services")
async def cat_services(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for k in ["fill_mod", "fill_db"]:
        builder.row(types.InlineKeyboardButton(text=f"{PRODUCTS[k]['name']} | {PRODUCTS[k]['price']}⭐", callback_data=f"buy_item:{k}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    await callback.message.edit_text("🛠 Услуги по настройке:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "cat_shop")
async def cat_shop(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for k in ["launcher", "mod"]:
        builder.row(types.InlineKeyboardButton(text=f"{PRODUCTS[k]['name']} | {PRODUCTS[k]['price']}⭐", callback_data=f"buy_item:{k}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main"))
    await callback.message.edit_text("🛒 Магазин ресурсов:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("buy_item:"))
async def buy_item(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    item = PRODUCTS[key]
    u_data = db_query("SELECT balance FROM users WHERE id = ?", (callback.from_user.id,), fetch=True)
    if not u_data: return
    u = u_data[0]
    
    if u[0] >= item['price']:
        new_bal = u[0] - item['price']
        db_query("UPDATE users SET balance = ? WHERE id = ?", (new_bal, callback.from_user.id))
        await callback.message.answer(f"✅ Успешная покупка: **{item['name']}**\n\n📦 Ссылка: {item['link']}\n💰 Остаток: {new_bal} ⭐", parse_mode="Markdown")
    else:
        await callback.answer(f"❌ Недостаточно ⭐! Нужно {item['price']}", show_alert=True)

@dp.callback_query(F.data == "free_jenny")
async def free_jenny(callback: types.CallbackQuery):
    u = db_query("SELECT jenny_used FROM users WHERE id = ?", (callback.from_user.id,), fetch=True)[0]
    if u[0] == 1:
        await callback.answer("❌ Ты уже получал бесплатную комплектацию!", show_alert=True)
    else:
        db_query("UPDATE users SET jenny_used = 1 WHERE id = ?", (callback.from_user.id,))
        await callback.message.answer("🎁 Твоя бесплатная комплектация Дженни готова!\n🔗 Ссылка: https://github.com/IrvenDaro/JennyPack")

@dp.message(Command("give"))
async def admin_give(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        _, uid, amt = message.text.split()
        db_query("UPDATE users SET balance = balance + ? WHERE id = ?", (int(amt), int(uid)))
        await message.answer(f"✅ Выдано {amt} ⭐ пользователю {uid}")
        try:
            await bot.send_message(uid, f"💰 Твой баланс пополнен на {amt} ⭐!")
        except: pass
    except: await message.answer("Ошибка! Юзай: `/give ID СУММА`")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())