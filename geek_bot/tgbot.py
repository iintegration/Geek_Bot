import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import psycopg2
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

import config

DATABASE_URL = config.URL

dp = Dispatcher(bot=Bot(config.BOT_TOKEN), storage=MemoryStorage())


class Form(StatesGroup):
    answer = State()
    current_question = State()


@dp.message_handler(CommandStart())
async def cmd_start(msg: Message, state: FSMContext) -> None:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Пройти опрос")
    await msg.answer(text="Привет, меня зовут Geeky, если хочешь пройти опрос, нажми соответствующуу кнопку", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "Пройти опрос")
async def start_quiz(msg: Message, state: FSMContext) -> None:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY order_number ASC")
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    async with state.proxy() as data:
        data['questions'] = questions
    await state.set_state(Form.current_question)
    await ask_question(msg, state)


async def ask_question(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        questions = data['questions']
    if not questions:
        await msg.answer(text="Спасибо за ответы!")
        await state.set_state(Form.answer)
        return
    question = questions[0]
    await msg.answer(text=question[2])
    async with state.proxy() as data:
        data['current_question'] = question[0]
    await state.set_state(Form.answer)


@dp.message_handler(state=Form.answer)
async def process_answer(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        question_id = data['current_question']
        user_id = msg.from_user.id
        answer = msg.text
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, answer, user_id) VALUES (%s, %s, %s)", (question_id, answer, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    async with state.proxy() as data:
        questions = data['questions']
        questions.pop(0)
    await state.set_state(Form.current_question)
    if questions:
        await ask_question(msg, state)
    else:
        await msg.answer(text="Спасибо за ответы!")


async def main() -> None:
    await dp.start_polling()


if __name__ == '__main__':
    print("Bot started...")
    asyncio.run(main())