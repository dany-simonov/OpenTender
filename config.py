import os
from datetime import timedelta
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///opentender.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Настройки CORS
    CORS_ORIGINS = ["http://localhost:3000"]
    
    # Настройки ограничения запросов
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Настройки парсера
    PARSER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    PARSER_TIMEOUT = 30  # seconds
    
    # Настройки планировщика
    SCHEDULER_UPDATE_INTERVAL = 3600  # 1 hour in seconds
    SCHEDULER_CLEANUP_INTERVAL = 86400  # 24 hours in seconds
    TENDER_RETENTION_DAYS = 30  # days to keep old tenders
    
    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настройки g4f
    G4F_MODEL = "gpt-3.5-turbo"
    G4F_TIMEOUT = 60  # seconds
    
    # Настройки безопасности
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # OAuth конфигурация
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': os.getenv('VK_APP_ID'),
            'secret': os.getenv('VK_APP_SECRET')
        },
        'yandex': {
            'id': os.getenv('YANDEX_APP_ID'),
            'secret': os.getenv('YANDEX_APP_SECRET')
        },
        'google': {
            'id': os.getenv('GOOGLE_APP_ID'),
            'secret': os.getenv('GOOGLE_APP_SECRET')
        }
    }
    
    @staticmethod
    def init_app(app):
        """Инициализация приложения с конфигурацией"""
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # В продакшене используем более строгие настройки безопасности
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    RATELIMIT_DEFAULT = "100 per day"
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Настройка логирования для продакшена
        import logging
        from logging.handlers import RotatingFileHandler
        
        handler = RotatingFileHandler(
            'logs/opentender.log',
            maxBytes=10000000,  # 10MB
            backupCount=10
        )
        handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        app.logger.addHandler(handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 