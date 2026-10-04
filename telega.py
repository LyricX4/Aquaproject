import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

BOT_TOKEN = "7834645581:AAE5SJxLabG55iPPKvHueUVpB-3NsUpcJQs"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users_data = {}


async def reminder_loop(chat_id: int, interval_hours: float):
    while True:
        await asyncio.sleep(interval_hours * 3600)

        try:
            await bot.send_message(chat_id, "Не забывай пить воду! Выпей стакан воды. 💧")
        except Exception as e:
            logging.error(f"Не удалось отправить напоминание: {e}")
            break


@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Привет! Я бот «Умное напоминание о воде».\n"
        "Я помогу тебе следить за водным балансом и вовремя пить воду.\n\n"
        "📋 Доступные команды:\n"
        "• /start — инструкция\n"
        "• /setreminder X — напоминания каждые X часов (например, /setreminder 2)\n"
        "• /drank X — отметить выпитую воду в мл (например, /drank 300)\n"
        "• /status — сколько воды выпито и сколько осталось."
    )
    await message.answer(welcome_text)


@dp.message(Command("setreminder"))
async def cmd_setreminder(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠ Забыли указать время. Пример: /setreminder 2")
        return

    try:
        hours = float(command.args)
        if hours <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠ Время должно быть нормальным числом больше нуля.")
        return

    user_id = message.from_user.id

    if user_id not in users_data:
        users_data[user_id] = {"drunk": 0, "goal": 2000, "task": None}

    if users_data[user_id]["task"]:
        users_data[user_id]["task"].cancel()

    task = asyncio.create_task(reminder_loop(message.chat.id, hours))
    users_data[user_id]["task"] = task

    await message.answer(f"✅ Готово! Буду напоминать пить воду каждые {hours} ч. ⏰")


@dp.message(Command("drank"))
async def cmd_drank(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("⚠ Укажите, сколько мл вы выпили. Пример: /drank 300")
        return

    try:
        amount = int(command.args)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠ Введите корректное число миллилитров.")
        return

    user_id = message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = {"drunk": 0, "goal": 2000, "task": None}

    users_data[user_id]["drunk"] += amount

    total_drunk = users_data[user_id]["drunk"]
    goal = users_data[user_id]["goal"]

    reply = f"💧 Плюс {amount} мл воды.\nВсего за сегодня: {total_drunk} мл из {goal} мл.\n\n"

    if total_drunk >= goal:
        reply += "🎉 Ура! Дневная норма воды выполнена! Отличная работа! 🏆"
    else:
        remaining = goal - total_drunk
        reply += f"📉 Чтобы закрыть норму, осталось выпить еще: {remaining} мл."

    await message.answer(reply)


@dp.message(Command("status"))
async def cmd_status(message: Message):
    user_id = message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = {"drunk": 0, "goal": 2000, "task": None}

    total_drunk = users_data[user_id]["drunk"]
    goal = users_data[user_id]["goal"]

    reply = f"📊 Ваш статус:\n• Выпито: {total_drunk} мл\n• Цель: {goal} мл\n"

    if total_drunk >= goal:
        reply += "\n🎉 Норма выполнена!"
    else:
        remaining = goal - total_drunk
        reply += f"\n💡 Осталось выпить: {remaining} мл."

    await message.answer(reply)


async def main():
    print("Бот успешно запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())