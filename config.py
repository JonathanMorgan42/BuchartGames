"""Application Configuration."""
import os
from datetime import timedelta
from pathlib import Path

# Get absolute path to project root
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    DEVADMIN_USERNAME = os.environ.get('DEVADMIN_USERNAME', 'devadmin')
    DEVADMIN_PASSWORD = os.environ.get('DEVADMIN_PASSWORD', 'devpassword')
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{INSTANCE_DIR}/gamenight_dev.db'
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{INSTANCE_DIR}/gamenight.db'
    SQLALCHEMY_ECHO = False

    # Session cookies should be secure since Cloudflare Tunnel provides HTTPS
    # Even though Flask receives HTTP, users connect via HTTPS
    SESSION_COOKIE_SECURE = True

    # Tell Flask to trust proxy headers from Cloudflare Tunnel
    PREFERRED_URL_SCHEME = 'https'

    # Don't enforce SSL-only CSRF tokens (Flask receives HTTP from tunnel)
    WTF_CSRF_SSL_STRICT = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
