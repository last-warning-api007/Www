import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
from pathlib import Path
from datetime import datetime, timedelta
import humanize

# Telegram Bot Token (Directly Added)
BOT_TOKEN = "7699996625:AAEyDyxrMJYCeXU8CMkQCzeTEW0EV5qjfAM"
bot = telebot.TeleBot(BOT_TOKEN)

# Welcome Keyboard
def create_welcome_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Channel", url="https://t.me/TEAMLBIN"),
        InlineKeyboardButton("Developer", url="https://t.me/hardhackar007")
    )
    return keyboard

# Upload to Catbox Function
def upload_to_catbox(file_path):
    try:
        # File size check (200MB limit)
        file_size = os.path.getsize(file_path)
        if file_size > 200 * 1024 * 1024:
            return {"status": "error", "message": "File size exceeds 200MB limit"}

        # Prepare file for upload
        files = {
            'fileToUpload': (Path(file_path).name, open(file_path, 'rb')),
            'reqtype': (None, 'fileupload')
        }

        # Upload to Catbox
        response = requests.post('https://catbox.moe/user/api.php', files=files, timeout=30)

        if response.status_code == 200:
            # Set expiry date (30 days)
            upload_date = datetime.now()
            expiry_date = upload_date + timedelta(days=30)

            return {
                "status": "success",
                "url": response.text.strip(),
                "file_name": Path(file_path).name,
                "file_size": humanize.naturalsize(file_size),
                "upload_date": upload_date.strftime("%Y-%m-%d %H:%M:%S"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
                "retention": "30 days minimum"
            }
        else:
            return {"status": "error", "message": f"Upload failed: {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        if 'files' in locals() and 'fileToUpload' in files:
            files['fileToUpload'][1].close()

# Start Command Handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(
        message.chat.id,
        "https://iili.io/2bnaLps.md.jpg",
        caption="""Welcome to Last Warning Bot! 🚀

Send me a file to upload and I'll return a shareable link.

Features:
✅ Uploads up to 200MB
✅ 30-day file retention
✅ Direct download links

Send a file to get started!""",
        reply_markup=create_welcome_keyboard()
    )

# Handle Document Uploads
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        # Notify the user
        status_message = bot.reply_to(message, "📥 Receiving your file...")

        # Download the file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save temporarily
        file_name = message.document.file_name
        temp_path = f"/tmp/{file_name}"

        with open(temp_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Uploading message
        bot.edit_message_text("⏳ Uploading to Catbox.moe...", status_message.chat.id, status_message.message_id)

        # Upload to Catbox
        result = upload_to_catbox(temp_path)

        # Delete temporary file
        os.remove(temp_path)

        # Send result
        if result["status"] == "success":
            response_text = f"""
✅ *Upload Successful!*

📁 *Name:* `{result['file_name']}`
📏 *Size:* `{result['file_size']}`
📅 *Uploaded:* `{result['upload_date']}`
🗓️ *Expires:* `{result['expiry_date']}`
🔗 *Download Link:* `{result['url']}`

_Send another file to get a new upload link!_
"""
            bot.edit_message_text(response_text, status_message.chat.id, status_message.message_id, parse_mode='Markdown')
        else:
            bot.edit_message_text(f"❌ Upload failed: {result['message']}", status_message.chat.id, status_message.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

# Catch-All Handler (For Text or Unknown Inputs)
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Please send a file to upload. Use /start for instructions.")

# Start the bot using Long Polling
if __name__ == "__main__":
    print("Bot is running with long polling...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
      
