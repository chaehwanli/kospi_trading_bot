import requests
from utils.logger import setup_logger

logger = setup_logger("TelegramBot")

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message):
        if not self.token or not self.chat_id:
            logger.warning("Telegram token or chat_id missing. Skipping message.")
            return

        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message
            }
            response = requests.post(self.base_url, data=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
