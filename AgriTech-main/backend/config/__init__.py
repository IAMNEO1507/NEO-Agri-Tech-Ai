import os
import logging

from dotenv import load_dotenv


load_dotenv(
    dotenv_path=os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    )
)


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}

_logger = logging.getLogger(__name__)


def _redis_available(url):
    """Check if Redis is reachable at *url*."""
    try:
        import redis as _redis
        r = _redis.Redis.from_url(url, socket_connect_timeout=1)
        r.ping()
        return True
    except Exception:
        return False


class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = _env_bool('DEBUG', False)
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///agritech.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Storage Configuration
    # Options: 'local', 's3'
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')
    
    # Local Storage Settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # S3 Settings
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL') # For MinIO
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL_ID = 'gemini-2.5-flash'
    
    # Weather API
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_API_URL = "https://api.weatherapi.com/v1"
    
    # Firebase
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID')
    FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID')

    # Redis & Caching
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour default

    @classmethod
    def _resolve_cache(cls):
        """Use RedisCache when Redis is reachable, else SimpleCache."""
        if _redis_available(cls.REDIS_URL):
            _logger.info('Redis is reachable – using RedisCache')
            return 'RedisCache', cls.REDIS_URL
        _logger.warning('Redis is NOT reachable – falling back to SimpleCache')
        return 'SimpleCache', None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.CACHE_TYPE, cls.CACHE_REDIS_URL = cls._resolve_cache()

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = _env_bool('DEBUG', True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///agritech_dev.db')
    SQLALCHEMY_ECHO = False  # Log SQL queries in development

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = _env_bool('DEBUG', False)
    @classmethod
    def init_app(cls, app):
        if not os.environ.get('GEMINI_API_KEY'):
            pass # raise RuntimeError("GEMINI_API_KEY is not set in production!")
        if not os.environ.get('DATABASE_URL'):
            pass # raise RuntimeError("DATABASE_URL is not set in production!")

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
