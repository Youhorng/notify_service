import os 
import logging 
from datetime import datetime 
import telegram  # type: ignore
from telegram.constants import ParseMode # type: ignore
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

class TelegramService():

    # Initialize the TelegramService with bot token and chat ID
    def __init__(self):
        # Get telegram settings from env
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None

        # Check if settings are provided
        if not self.token or not self.chat_id:
            logging.error("Telegram bot token or chat ID is not set.")

        else:
            try:
                # Initialize the telegram bot
                self.bot = telegram.Bot(token=self.token)
                logging.info("Telegram bot initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Telegram bot: {e}")
    
    # Send fraut alert to telegram bot
    async def send_fraud_alert(self, data):
        try:
            # Format message for Telegram
            message = self.format_fraud_message(data)
            
            # If bot is not configured, simulate sending
            if not self.bot or not self.chat_id:
                logging.info(f"SIMULATION: Telegram message would be sent:\n{message}")
                return {
                    "success": True,
                    "message_id": f"simulated-{datetime.now().timestamp()}",
                    "content": message
                }
            
            # Send the actual message
            response = await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            logging.info(f"Sent fraud alert to Telegram. Message ID: {response.message_id}")
            
            return {
                "success": True,
                "message_id": str(response.message_id),
                "content": message
            }
            
        except Exception as e:
            logging.error(f"Error sending Telegram notification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    

    # Format the telegram message
    def format_fraud_message(self, data):
        fraud_probability = data.get("fraud_probability", 0)
        risk_level = self.get_risk_level(fraud_probability)
        emoji = self.get_emoji_for_risk(risk_level)

        # Format amount with 2 decimal places
        amount = f"${data.get('transaction_amount', 0):.2f}"
        
        # Format probability as percentage
        probability_pct = f"{fraud_probability * 100:.1f}%"
        
        # Create the message
        return f"""
{emoji} <b>FRAUD ALERT</b> {emoji}

<b>Transaction Number:</b> {data.get('transaction_number', 'Unknown')}
<b>Amount:</b> {amount}
<b>Fraud Probability:</b> {probability_pct}
<b>Risk Level:</b> {risk_level}
<b>Category:</b> {data.get('category', 'N/A')}
<b>Transaction Location:</b> {data.get('transaction_location', 'N/A')}
<b>Time:</b> {"Night" if data.get('is_nighttime') else "Day"}

<i>Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""


    # Determine the risk level based on probability
    def get_risk_level(self, probability):
        if probability >= 0.8:
            return "CRITICAL"
        elif probability >= 0.7:
            return "HIGH"
        else:
            return "MEDIUM"
    

    # Get emoji based on risk level
    def get_emoji_for_risk(self, risk_level):
        emojis = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "ℹ️"
        }

        return emojis.get(risk_level)

# Create instance 
telegram_service = TelegramService()