import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.event.bases import TelegramObject, CancelHandler
from aiogram.types import FSInputFile
from keep_alive import keep_alive  # Uncomment if needed

# Bot initialization
bot = Bot(token='6778014003:AAHsZzEKJ7hFWeBy5f6_ZCjptMUbAOpvlew')
dp = Dispatcher(storage=MemoryStorage())

CHANNEL_IDs = ['-1002195396899', '-1001814955117']  # List of channel IDs

async def generate_channel_buttons():
    buttons = []
    for CHANNEL_ID in CHANNEL_IDs:
        chat = await bot.get_chat(CHANNEL_ID)
        buttons.append([InlineKeyboardButton(text=f"Join our Channel {chat.title}", url=f"https://t.me/{chat.username or CHANNEL_ID}")])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data='check')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def not_joined_channels(CHANNEL_ID):
    buttons = []
    chat = await bot.get_chat(CHANNEL_ID)
    buttons.append([InlineKeyboardButton(text=f"Join our Channel {chat.title}", url=f"https://t.me/{chat.username or CHANNEL_ID}")])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data='check')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start(message: Message):
    channels = await generate_channel_buttons()
    user_lan = message.from_user.language_code
    if user_lan == 'en':
        await message.answer('Welcome to the tournament of Elyor', reply_markup=channels)
    else:
        await message.answer('Salom, Elyorning musobaqasiga xush kelibsiz', reply_markup=channels)


@dp.callback_query(lambda query: query.data == 'check')
async def check(query: CallbackQuery):
    user_id = query.from_user.id
    not_joined = []

    for CHANNEL_ID in CHANNEL_IDs:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            not_joined.append(CHANNEL_ID)

    if not_joined:
        buttons = []
        for channel in not_joined:
            chat = await bot.get_chat(channel)
            buttons.append([InlineKeyboardButton(text=f"Join our Channel {chat.title}",
                                                 url=f"https://t.me/{chat.username or channel}")])
        buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data='check')])

        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.answer("Please join the channels first.", reply_markup=markup)
    else:
        file = 'money.py'
        document = FSInputFile(file)
        await query.message.answer_document(document)
        await query.message.answer("Thank you for joining the channel!")


class TestMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        print("Middleware before handler: Request received")
        channels = await generate_channel_buttons()

        if isinstance(event, Message):  # Ensure the event is a Message type
            user_id = event.from_user.id
            for CHANNEL_ID in CHANNEL_IDs:
                chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

                if chat_member.status in ['left', 'kicked']:
                    not_joined_channel = await not_joined_channels(CHANNEL_ID)
                    await bot.delete_message(chat_id=event.message.chat.id, message_id=event.message_id-1)
                    await event.answer("Please join the channels first.", reply_markup=not_joined_channel)
                    raise CancelHandler()

        result = await handler(event, data)
        print("Middleware after handler: Response sent")
        return result

dp.update.middleware(TestMiddleware())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # keep_alive()  # Uncomment if needed
        print('working')
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
