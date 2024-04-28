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
        data['current_question_index'] = 0  # Добавлено
    await state.set_state(Form.current_question)
    await ask_question(msg, state)


async def ask_question(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        questions = data['questions']
        current_question_index = data['current_question_index']  # Добавлено
    if current_question_index >= len(questions):  # Изменено
        await msg.answer(text="Спасибо за ответы!")
        await state.set_state(Form.answer)
        return
    question = questions[current_question_index]  # Изменено
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
        questions = data['questions']
        current_question_index = data['current_question_index']  # Добавлено

    # Проверка, является ли это первым вопросом и ответ меньше 5
    if current_question_index == 0 and int(answer) < 5:  # Изменено
        await msg.answer(text="Ваш ответ на первый вопрос меньше 5, тест завершен.")
        await state.reset_state()
        return

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO answers (question_id, answer, user_id) VALUES (%s, %s, %s)", (question_id, answer, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    async with state.proxy() as data:
        data['current_question_index'] += 1  # Увеличиваем индекс текущего вопроса
    await state.set_state(Form.current_question)
    await ask_question(msg, state)


async def main() -> None:
    await dp.start_polling()


if __name__ == '__main__':
    print("Bot started...")
    asyncio.run(main())