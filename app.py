from flask import Flask, request, jsonify
import requests
import os
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

app = Flask(__name__)

# Your Truecaller API Key
TRUECALLER_API_KEY = '5BO640155545a4dc345129ce8b3de7cbb3093'
# Your Telegram Bot Token
TELEGRAM_BOT_TOKEN = '7065470365:AAH84EEwdlbq2PtGN3xazmFjtjG_KxyHlPY'
# Telegram Bot Instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Set up Dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

def fetch_info_from_truecaller(phone_number):
    url = f'https://api.truecaller.com/v1/phone/{phone_number}'
    headers = {
        'Authorization': f'Bearer {TRUECALLER_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Unable to fetch information'}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a phone number to get information!')

def handle_message(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.text.strip()
    
    # Validate phone number (basic check)
    if not phone_number.isdigit() or len(phone_number) < 10:
        update.message.reply_text('Please send a valid phone number.')
        return

    info = fetch_info_from_truecaller(phone_number)
    
    # Check for errors in the response
    if 'error' in info:
        update.message.reply_text(info['error'])
    else:
        # Format the response as needed
        response_message = f"Information for {phone_number}:\n"
        response_message += f"Name: {info.get('name', 'N/A')}\n"
        response_message += f"Carrier: {info.get('carrier', 'N/A')}\n"
        response_message += f"Location: {info.get('location', 'N/A')}\n"
        update.message.reply_text(response_message)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok', 200

def set_webhook():
    webhook_url = f'https://truecallerns.onrender.com/webhook'
    bot.setWebhook(webhook_url)

if __name__ == '__main__':
    set_webhook()  # Set the webhook when the app starts
    app.run(host='0.0.0.0', port=5000)

