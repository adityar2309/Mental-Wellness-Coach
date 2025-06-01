"""
Mental Wellness Coach - Flask Configuration

Configuration classes for different environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key')
    
    # Database Configuration - Using SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wellness_coach.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://:wellness_redis_pass@localhost:6379')
    
    # AI Configuration
    ASI_ONE_API_KEY = os.getenv('ASI_ONE_API_KEY')
    ASI_ONE_API_URL = os.getenv('ASI_ONE_API_URL', 'https://api.asi.one/v1')
    ASI_ONE_MODEL = os.getenv('ASI_ONE_MODEL', 'asi-one-main')
    ASI_ONE_MAX_TOKENS = int(os.getenv('ASI_ONE_MAX_TOKENS', '2048'))
    ASI_ONE_TEMPERATURE = float(os.getenv('ASI_ONE_TEMPERATURE', '0.7'))
    
    # Fetch.ai Configuration
    FETCH_AI_AGENT_KEY = os.getenv('FETCH_AI_AGENT_KEY')
    FETCH_AI_MAILBOX_KEY = os.getenv('FETCH_AI_MAILBOX_KEY')
    FETCH_AI_NETWORK = os.getenv('FETCH_AI_NETWORK', 'testnet')
    
    # Security Configuration
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev_32_char_encryption_key_here')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Mental Health Configuration
    CRISIS_HOTLINE_US = os.getenv('CRISIS_HOTLINE_US', '988')
    CRISIS_HOTLINE_UK = os.getenv('CRISIS_HOTLINE_UK', '116123')
    CRISIS_ESCALATION_EMAIL = os.getenv('CRISIS_ESCALATION_EMAIL', 'crisis@mentalwellnesscoach.ai')
    
    # Feature Flags
    FEATURE_MOOD_CHECKIN = os.getenv('FEATURE_MOOD_CHECKIN', 'true').lower() == 'true'
    FEATURE_JOURNALING = os.getenv('FEATURE_JOURNALING', 'true').lower() == 'true'
    FEATURE_COPING_TOOLKIT = os.getenv('FEATURE_COPING_TOOLKIT', 'true').lower() == 'true'
    FEATURE_CRISIS_DETECTION = os.getenv('FEATURE_CRISIS_DETECTION', 'true').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_PATH', './uploads')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://:wellness_redis_pass@localhost:6379')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries
    MOCK_AI_RESPONSES = os.getenv('MOCK_AI_RESPONSES', 'true').lower() == 'true'
    
    # Relaxed security for development
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    # SQLite-specific settings for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wellness_coach_dev.db')

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # SQLite-specific settings for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wellness_coach_prod.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        # SQLite doesn't need pool size settings
    }
    
    # Production logging
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Test database - in-memory SQLite for fast testing
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Mock everything for testing
    MOCK_AI_RESPONSES = True
    
    # Fast JWT expiry for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('NODE_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig) 