"""Stripe configuration management for TicTacToe billing."""
import os
from typing import Optional
from enum import Enum


class StripeEnvironment(Enum):
    """Stripe environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class StripeConfig:
    """Stripe API configuration handler."""
    
    def __init__(self, environment: Optional[str] = None):
        """Initialize Stripe configuration.
        
        Args:
            environment: Override environment (development/production).
                        Defaults to STRIPE_ENVIRONMENT env var or 'development'.
        """
        self.environment = environment or os.getenv(
            "STRIPE_ENVIRONMENT", 
            StripeEnvironment.DEVELOPMENT.value
        )
        self._validate_environment()
        self._load_keys()
    
    def _validate_environment(self) -> None:
        """Validate environment setting."""
        valid_envs = [e.value for e in StripeEnvironment]
        if self.environment not in valid_envs:
            raise ValueError(
                f"Invalid environment: {self.environment}. "
                f"Must be one of {valid_envs}"
            )
    
    def _load_keys(self) -> None:
        """Load Stripe API keys from environment variables."""
        if self.environment == StripeEnvironment.PRODUCTION.value:
            self.secret_key = os.getenv("STRIPE_LIVE_SECRET_KEY")
            self.publishable_key = os.getenv("STRIPE_LIVE_PUBLISHABLE_KEY")
            self.webhook_secret = os.getenv("STRIPE_LIVE_WEBHOOK_SECRET")
        else:
            self.secret_key = os.getenv("STRIPE_TEST_SECRET_KEY")
            self.publishable_key = os.getenv("STRIPE_TEST_PUBLISHABLE_KEY")
            self.webhook_secret = os.getenv("STRIPE_TEST_WEBHOOK_SECRET")
        
        self._validate_keys()
    
    def _validate_keys(self) -> None:
        """Validate that required keys are present."""
        if not self.secret_key:
            raise ValueError(
                f"Missing Stripe secret key for {self.environment} environment. "
                f"Set STRIPE_{'LIVE' if self.is_production else 'TEST'}_SECRET_KEY"
            )
        
        if not self.publishable_key:
            raise ValueError(
                f"Missing Stripe publishable key for {self.environment} environment. "
                f"Set STRIPE_{'LIVE' if self.is_production else 'TEST'}_PUBLISHABLE_KEY"
            )
        
        # Validate key format
        expected_prefix = "sk_live_" if self.is_production else "sk_test_"
        if not self.secret_key.startswith(expected_prefix):
            raise ValueError(
                f"Invalid secret key format for {self.environment}. "
                f"Expected prefix: {expected_prefix}"
            )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == StripeEnvironment.PRODUCTION.value
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == StripeEnvironment.DEVELOPMENT.value
    
    def get_api_version(self) -> str:
        """Get Stripe API version to use."""
        return os.getenv("STRIPE_API_VERSION", "2023-10-16")
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary (excluding sensitive data)."""
        return {
            "environment": self.environment,
            "is_production": self.is_production,
            "has_secret_key": bool(self.secret_key),
            "has_publishable_key": bool(self.publishable_key),
            "has_webhook_secret": bool(self.webhook_secret),
            "publishable_key": self.publishable_key,
            "api_version": self.get_api_version()
        }


# Global configuration instance
_config: Optional[StripeConfig] = None


def get_stripe_config() -> StripeConfig:
    """Get or create global Stripe configuration instance."""
    global _config
    if _config is None:
        _config = StripeConfig()
    return _config


def initialize_stripe_config(environment: Optional[str] = None) -> StripeConfig:
    """Initialize or reinitialize Stripe configuration.
    
    Args:
        environment: Override environment setting.
    
    Returns:
        Configured StripeConfig instance.
    """
    global _config
    _config = StripeConfig(environment=environment)
    return _config