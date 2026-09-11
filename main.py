import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


# =========================================================
# BOT TOKEN
# =========================================================

BOT_TOKEN = "8919732968:AAHWSHzaFe_QlJkjC8846oyCvM3MYRO0JqE"


# =========================================================
# BOT VA DISPATCHER
# =========================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================================================
# KOREYS HARFLARI
# =========================================================

letters = [
    ("ㅏ", "a"),
    ("ㅑ", "ya"),
    ("ㅓ", "o'"),
    ("ㅕ", "yo'"),
    ("ㅗ", "o"),
    ("ㅛ", "yo"),
    ("ㅜ", "u"),
    ("ㅠ", "yu"),
    ("ㅡ", "eu"),
    ("ㅣ", "i"),
    ("ㅐ", "eh"),
    ("ㅒ", "yeh"),
    ("ㅔ", "e"),
    ("ㅖ", "ye"),
    ("ㅘ", "va"),
    ("ㅙ", "veh"),
    ("ㅚ", "vi"),
    ("ㅝ", "vo"),
    ("ㅞ", "ve"),
    ("ㅢ", "ui"),
]


# =========================================================
# FOYDALANUVCHI MA'LUMOTLARI
# =========================================================

users = {}


# =========================================================
# BOSHLANG'ICH TUGMALAR
# =========================================================

def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Testni boshlash")
            ],
            [
                KeyboardButton(text="❌ Testni to'xtatish")
            ]
        ],
        resize_keyboard=True
    )


# =========================================================
# TEST TUGMALARI
# =========================================================

def test_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=options[0]),
                KeyboardButton(text=options[1])
            ],
            [
                KeyboardButton(text=options[2])
            ],
            [
                KeyboardButton(text="❌ Testni to'xtatish")
            ]
        ],
        resize_keyboard=True
    )


# =========================================================
# STATISTIKA
# =========================================================

def statistics(user_id):

    data = users[user_id]

    total = data["total"]
    correct = data["correct"]
    wrong = data["wrong"]

    if total > 0:
        percent = round(correct / total * 100, 1)
    else:
        percent = 0

    return (
        "📊 <b>TEST STATISTIKASI</b>\n\n"
        f"📝 Jami ishlangan: {total}\n"
        f"✅ To'g'ri: {correct}\n"
        f"❌ Noto'g'ri: {wrong}\n"
        f"📈 Natija: {percent}%"
    )


# =========================================================
# KEYINGI SAVOL
# =========================================================

async def next_question(message: Message):

    user_id = message.from_user.id
    data = users[user_id]

    # Test to'xtatilgan bo'lsa savol bermaydi
    if not data["testing"]:
        return

    # 20 ta savol tugasa yana aralashtirib boshlaydi
    if data["question_index"] >= len(data["questions"]):

        data["questions"] = letters.copy()
        random.shuffle(data["questions"])

        data["question_index"] = 0

    # Savol
    letter, correct_answer = data["questions"][data["question_index"]]

    # Noto'g'ri variantlarni olish
    wrong_answers = [
        answer
        for _, answer in letters
        if answer != correct_answer
    ]

    # 2 ta noto'g'ri variant
    options = random.sample(wrong_answers, 2)

    # To'g'ri variantni qo'shamiz
    options.append(correct_answer)

    # Variantlarni aralashtiramiz
    random.shuffle(options)

    # Saqlaymiz
    data["correct_answer"] = correct_answer
    data["current_letter"] = letter

    await message.answer(
        f"📝 <b>Savol</b>\n\n"
        f"🇰🇷 <b>{letter}</b>\n\n"
        f"Bu harf qanday o'qiladi?",
        reply_markup=test_keyboard(options)
    )


# =========================================================
# /START
# =========================================================

@dp.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id

    users[user_id] = {
        "testing": False,
        "questions": [],
        "question_index": 0,
        "total": 0,
        "correct": 0,
        "wrong": 0,
        "correct_answer": None,
        "current_letter": None
    }

    await message.answer(
        "🇰🇷 <b>KOREYS ALIFBOSI TESTI</b>\n\n"
        "Men sizga koreys harfini ko'rsataman.\n"
        "Siz uning to'g'ri o'qilishini tanlaysiz.\n\n"
        "⚠️ Test siz to'xtatmaguningizcha davom etadi.\n\n"
        "Testni boshlaysizmi?",
        reply_markup=start_keyboard()
    )


# =========================================================
# TESTNI BOSHLASH
# =========================================================

@dp.message(F.text == "✅ Testni boshlash")
async def start_test(message: Message):

    user_id = message.from_user.id

    questions = letters.copy()
    random.shuffle(questions)

    users[user_id] = {
        "testing": True,
        "questions": questions,
        "question_index": 0,
        "total": 0,
        "correct": 0,
        "wrong": 0,
        "correct_answer": None,
        "current_letter": None
    }

    await message.answer(
        "🚀 <b>TEST BOSHLANDI!</b>\n\n"
        "⚠️ Testni to'xtatmaguningizcha davom etadi."
    )

    await next_question(message)


# =========================================================
# TESTNI TO'XTATISH
# =========================================================

@dp.message(F.text == "❌ Testni to'xtatish")
async def stop_test(message: Message):

    user_id = message.from_user.id

    if user_id not in users:

        await message.answer(
            "Avval /start bosing.",
            reply_markup=start_keyboard()
        )

        return

    data = users[user_id]

    if not data["testing"]:

        await message.answer(
            "Hozir test ishlanmayapti.",
            reply_markup=start_keyboard()
        )

        return

    # Testni to'xtatamiz
    data["testing"] = False

    await message.answer(
        "⛔ <b>TEST TO'XTATILDI!</b>\n\n"
        + statistics(user_id),
        reply_markup=start_keyboard()
    )


# =========================================================
# JAVOBNI TEKSHIRISH
# =========================================================

@dp.message()
async def answer_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in users:
        return

    data = users[user_id]

    # Test ishlamayotgan bo'lsa
    if not data["testing"]:
        return

    answer = message.text

    # To'xtatish tugmasi alohida handlerda ishlaydi
    if answer == "❌ Testni to'xtatish":
        return

    correct_answer = data["correct_answer"]
    letter = data["current_letter"]

    data["total"] += 1

    # =====================================================
    # TO'G'RI
    # =====================================================

    if answer == correct_answer:

        data["correct"] += 1

        await message.answer(
            f"✅ <b>TO'G'RI!</b>\n\n"
            f"🇰🇷 {letter} → <b>{correct_answer}</b>"
        )

    # =====================================================
    # XATO
    # =====================================================

    else:

        data["wrong"] += 1

        await message.answer(
            f"❌ <b>XATO!</b>\n\n"
            f"🇰🇷 Harf: <b>{letter}</b>\n\n"
            f"✅ To'g'ri javob: <b>{correct_answer}</b>\n"
            f"❌ Sizning javobingiz: <b>{answer}</b>"
        )

    # Keyingi savol
    data["question_index"] += 1

    await next_question(message)


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

async def main():

    print("🇰🇷 Koreys test bot ishga tushdi!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
