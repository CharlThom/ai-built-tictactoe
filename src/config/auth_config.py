import os
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    """Authentication configuration settings"""
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    # OAuth2 Configuration
    OAUTH2_GOOGLE_CLIENT_ID = os.getenv('OAUTH2_GOOGLE_CLIENT_ID')
    OAUTH2_GOOGLE_CLIENT_SECRET = os.getenv('OAUTH2_GOOGLE_CLIENT_SECRET')
    OAUTH2_GITHUB_CLIENT_ID = os.getenv('OAUTH2_GITHUB_CLIENT_ID')
    OAUTH2_GITHUB_CLIENT_SECRET = os.getenv('OAUTH2_GITHUB_CLIENT_SECRET')
    
    # Security Settings
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', '12'))
    PASSWORD_MIN_LENGTH = 8
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.JWT_SECRET_KEY:
            errors.append('JWT_SECRET_KEY environment variable is required')
        elif cls.JWT_SECRET_KEY == 'dev-secret-key-change-in-production':
            if os.getenv('FLASK_ENV') == 'production':
                errors.append('JWT_SECRET_KEY must be changed in production')
        
        if len(cls.JWT_SECRET_KEY or '') < 32:
            errors.append('JWT_SECRET_KEY should be at least 32 characters long')
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


# Example .env file content (create this file in project root)
ENV_TEMPLATE = """
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-long-change-this
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2 Providers
OAUTH2_GOOGLE_CLIENT_ID=your-google-client-id
OAUTH2_GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTH2_GITHUB_CLIENT_ID=your-github-client-id
OAUTH2_GITHUB_CLIENT_SECRET=your-github-client-secret

# Security
BCRYPT_LOG_ROUNDS=12

# Application
FLASK_ENV=development
"""