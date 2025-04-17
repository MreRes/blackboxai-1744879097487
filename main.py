import threading
from src.dashboard.app import app
from src.bot.whatsapp_handler import WhatsAppBot
from src.utils.config import Config
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def start_whatsapp_bot():
    """Start the WhatsApp bot in a separate thread"""
    try:
        bot = WhatsAppBot()
        bot.start()
        bot.listen_for_messages()
    except Exception as e:
        logger.error(f"WhatsApp bot error: {str(e)}")
    finally:
        if bot:
            bot.cleanup()

def main():
    """Main entry point of the application"""
    try:
        # Start WhatsApp bot in a separate thread if enabled
        if Config.WHATSAPP_ENABLED:
            logger.info("Starting WhatsApp bot...")
            whatsapp_thread = threading.Thread(target=start_whatsapp_bot)
            whatsapp_thread.daemon = True
            whatsapp_thread.start()
            logger.info("WhatsApp bot started successfully")

        # Start Flask dashboard
        logger.info("Starting Flask dashboard...")
        app.run(host='0.0.0.0', port=8000, debug=Config.DEBUG)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
