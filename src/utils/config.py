import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', True)
    
    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'financial.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WhatsApp Bot Configuration
    WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'true').lower() == 'true'
    
    # Financial Settings
    DEFAULT_CURRENCY = 'Rp'  # Indonesian Rupiah
    SAVINGS_ALLOCATION_PERCENTAGE = 20  # Default percentage of income to allocate to savings
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Financial APIs
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', '')
    
    # AI Model Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # For financial advice generation
    AI_TEMPERATURE = 0.7
    AI_MAX_TOKENS = 500
    
    # Financial Planning Constants
    MIN_EMERGENCY_FUND = 6  # months of expenses
    RECOMMENDED_SAVINGS_RATE = 0.2  # 20% of income
    INVESTMENT_THRESHOLD = 10000000  # Rp. 10,000,000
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Categories for transactions
    EXPENSE_CATEGORIES = [
        'Housing',
        'Transportation',
        'Food',
        'Utilities',
        'Healthcare',
        'Entertainment',
        'Shopping',
        'Education',
        'Savings',
        'Other'
    ]

    INCOME_CATEGORIES = [
        'Salary',
        'Business',
        'Investment',
        'Freelance',
        'Other'
    ]

    @staticmethod
    def init_app(app):
        """Initialize application with config settings"""
        app.config.from_object(__class__)
