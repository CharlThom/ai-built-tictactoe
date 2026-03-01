from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from src.database import Base


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PREMIUM = "premium"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Stripe integration fields
    stripe_customer_id = Column(String(255), unique=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_price_id = Column(String(255))
    
    # Subscription metadata
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    usage = relationship("SubscriptionUsage", back_populates="subscription", uselist=False, cascade="all, delete-orphan")

    def is_premium(self) -> bool:
        """Check if subscription is premium and active"""
        return self.tier == SubscriptionTier.PREMIUM and self.status == SubscriptionStatus.ACTIVE

    def can_play_unlimited(self) -> bool:
        """Check if user can play unlimited games"""
        return self.is_premium()

    def should_show_ads(self) -> bool:
        """Check if ads should be shown to user"""
        return not self.is_premium()


class SubscriptionUsage(Base):
    """Track subscription usage and limits"""
    __tablename__ = "subscription_usage"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, unique=True, index=True)
    
    # Usage tracking
    games_played_today = Column(Integer, default=0, nullable=False)
    games_played_this_month = Column(Integer, default=0, nullable=False)
    last_game_played_at = Column(DateTime, nullable=True)
    
    # Reset tracking
    daily_reset_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    monthly_reset_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage")

    def can_play_game(self, free_daily_limit: int = 10) -> bool:
        """Check if user can play a game based on tier and usage"""
        if self.subscription.is_premium():
            return True
        
        # Reset daily counter if needed
        now = datetime.utcnow()
        if (now - self.daily_reset_at).days >= 1:
            self.games_played_today = 0
            self.daily_reset_at = now
        
        return self.games_played_today < free_daily_limit

    def increment_usage(self):
        """Increment game usage counters"""
        now = datetime.utcnow()
        
        # Reset daily counter if needed
        if (now - self.daily_reset_at).days >= 1:
            self.games_played_today = 0
            self.daily_reset_at = now
        
        # Reset monthly counter if needed
        if (now.year > self.monthly_reset_at.year or 
            (now.year == self.monthly_reset_at.year and now.month > self.monthly_reset_at.month)):
            self.games_played_this_month = 0
            self.monthly_reset_at = now
        
        self.games_played_today += 1
        self.games_played_this_month += 1
        self.last_game_played_at = now
        self.updated_at = now