import os

from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

BACK_BUTTON = "⬅️ Orqaga"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")

# ================= DATA =================
DATA = {
    "Arduino": {
        "text": """🔵 Arduino haqida:

Arduino — ochiq manbali mikrokontroller platformasi.

📌 ATmega328P chip
📌 14 digital pin
📌 6 analog pin
📌 5V ishlash kuchlanishi

Robototexnika va IoT loyihalarda ishlatiladi.""",
        "image": "arduino.png"
    },
    "DHT11": {"text": "🟢 DHT11 harorat va namlik sensori.\nVCC→5V\nGND→GND\nDATA→D2", "image": "dht11.jpg"},
    "DHT22": {"text": "🟢 DHT22 aniqligi yuqori sensor.\nVCC→5V\nGND→GND\nDATA→D2", "image": "dht22.jpg"},
    "Servo": {"text": "🟢 Servo motor.\nQizil→5V\nJigarrang→GND\nSariq→D9", "image": "servo.jpg"},
    "Stepper": {"text": "🟢 Stepper (ULN2003).\nIN1→D8\nIN2→D9\nIN3→D10\nIN4→D11", "image": "stepper.jpg"},
    "Bluetooth": {"text": "🟢 HC-05 Bluetooth.\nVCC→5V\nGND→GND\nTX→RX\nRX→TX", "image": "bluetooth.jpg"},
    "ESP32": {"text": """🔵 ESP32 haqida:

WiFi + Bluetooth chip
240MHz dual-core
3.3V logika
Ko‘plab GPIO pinlar""", "image": "esp32.jpg"},
    "RFID": {"text": "🟢 RFID RC522.\nSDA→D10\nSCK→D13\nMOSI→D11\nMISO→D12\nRST→D9", "image": "rfid.png"},
    "IR control": {"text": "🟢 IR Receiver.\nVCC→5V\nGND→GND\nOUT→D2", "image": "ir_control.jpg"},
    "LED": {"text": "🟢 LED ulanishi.\nAnod→220Ω→D13\nKatod→GND", "image": "led.jpg"}
}

# ================= MENU =================
def build_keyboard(button_names: list[str], include_back: bool = False) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in button_names]
    if include_back:
        keyboard.append([InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)])
    return InlineKeyboardMarkup(keyboard)

def main_menu() -> InlineKeyboardMarkup:
    return build_keyboard(list(DATA.keys()))

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command or reply-button 'start'.

    The first time the user sends "/start" we reply with **a reply
    keyboard** containing a single "start" button (one-time).
    When the user later sends plain text "start" (by tapping the button)
    we show the inline inline menu and explicitly remove the reply
    keyboard so it doesn't linger.
    """
    text = update.message.text or ""
    if text.strip().lower() == "/start":
        # first interaction: send reply keyboard
        await update.message.reply_text(
            'Botni ishga tushirish uchun pastdagi "Boshlash 🚀" tugmasini bosing.',
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Boshlash 🚀")]],
                resize_keyboard=True,
                one_time_keyboard=True
            ),
        )
        return

    # pressed reply-keyboard "boshlash" button (case-insensitive)
    await update.message.reply_text(
        "📚 Modulni tanlang:",
        reply_markup=main_menu()
    )
    # remove any (possibly stale) reply keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="", reply_markup=ReplyKeyboardRemove()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ----------------- BACK BUTTON -----------------
    if data == BACK_BUTTON:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📚 Modulni tanlang:",
            reply_markup=main_menu()
        )
        return

    module = DATA.get(data)
    if not module:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Kutilmagan xato. Iltimos, /start yoki boshlash tugmasini bosing.",
            reply_markup=main_menu()
        )
        return

    try:
        await query.message.delete()
    except Exception:
        pass

    image_path = os.path.join(IMAGE_DIR, module["image"])
    if os.path.isfile(image_path):
        with open(image_path, "rb") as f:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=f,
                caption=module["text"],
                reply_markup=build_keyboard([], include_back=True)
            )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=module["text"],
            reply_markup=build_keyboard([], include_back=True)
        )

# ================= MAIN =================
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN muhit o'zgaruvchisi o'rnatilmagan")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # text message containing "start" (case insensitive) triggers same handler
    app.add_handler(
        MessageHandler(filters.Regex(r"(?i)^Boshlash 🚀$"), start)
    )
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()