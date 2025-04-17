import threading
from src.dashboard.app import app, db
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

def init_database():
    """Initialize database and create tables"""
    try:
        logger.info("Initializing database...")
        with app.app_context():
            # Drop all tables and recreate them
            db.drop_all()
            db.create_all()
            
            # Create test user
            from src.dashboard.app import User, Transaction
            from datetime import datetime, timedelta
            
            test_user = User.query.filter_by(username="test_user").first()
            if not test_user:
                test_user = User(username="test_user")
                db.session.add(test_user)
                db.session.commit()
            
            # Add sample transactions if none exist
            if not Transaction.query.first():
                # Sample income transactions
                transactions = [
                    Transaction(
                        user_id=test_user.id,
                        amount=8000000,
                        category="salary",
                        transaction_type="income",
                        description="Gaji Bulanan",
                        date=datetime.now() - timedelta(days=i)
                    ) for i in range(0, 30, 30)
                ]
                
                # Sample expense transactions
                expense_data = [
                    ("housing", 2500000, "Sewa Apartemen"),
                    ("food", 1500000, "Belanja Bulanan"),
                    ("transportation", 800000, "Bensin dan Transportasi"),
                    ("utilities", 500000, "Listrik dan Air"),
                    ("entertainment", 700000, "Hiburan")
                ]
                
                for category, amount, desc in expense_data:
                    transactions.append(
                        Transaction(
                            user_id=test_user.id,
                            amount=amount,
                            category=category,
                            transaction_type="expense",
                            description=desc,
                            date=datetime.now() - timedelta(days=1)
                        )
                    )
                
                db.session.add_all(transactions)
                db.session.commit()
            
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

def main():
    """Main entry point of the application"""
    try:
        # Initialize database first
        init_database()
        
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
