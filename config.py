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

    # Session cookie settings (HTTPOnly for security)
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # CSRF Protection settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Admin credentials
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

    # Development uses Lax (works fine for local HTTP)
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False


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

    # Cookie settings for HTTPS (via Cloudflare Tunnel)
    # SameSite='None' allows cookies in embedded browsers (Snapchat, Instagram, etc.)
    # Requires Secure=True (HTTPS) to work
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_DOMAIN = None  # Don't restrict to a specific domain (critical for mobile)

    # Prevent large session cookies (mobile browsers reject them)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_TYPE = 'filesystem'  # Store sessions on disk instead of cookies
    SESSION_FILE_DIR = INSTANCE_DIR / 'flask_session'  # Store in instance directory
    SESSION_PERMANENT = True  # Use PERMANENT_SESSION_LIFETIME
    SESSION_USE_SIGNER = True  # Sign session cookie for extra security

    # CSRF cookie settings - must match session cookie settings
    WTF_CSRF_SSL_STRICT = False  # Flask receives HTTP from Cloudflare Tunnel
    WTF_CSRF_COOKIE_SECURE = True
    WTF_CSRF_COOKIE_SAMESITE = 'None'
    WTF_CSRF_COOKIE_HTTPONLY = False  # Must be False so JS can't read it but form can submit it
    WTF_CSRF_COOKIE_DOMAIN = None  # Match session cookie domain

    # Additional CSRF settings for mobile/in-app browsers
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour (instead of None) to reduce cookie size
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']  # Don't check GET requests

    # Tell Flask to trust proxy headers from Cloudflare Tunnel
    PREFERRED_URL_SCHEME = 'https'

    # Application root for proper URL generation behind proxy
    APPLICATION_ROOT = '/'


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
