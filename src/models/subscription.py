from enum import Enum
from src.database import db
from datetime import datetime


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    PAST_DUE = 'past_due'
    INCOMPLETE = 'incomplete'
    TRIALING = 'trialing'
    FREE = 'free'


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration."""
    FREE = 'free'
    PREMIUM = 'premium'
    PRO = 'pro'


class Subscription(db.Model):
    """Subscription model for managing user subscriptions."""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Stripe identifiers
    stripe_customer_id = db.Column(db.String(255), unique=True, index=True)
    stripe_subscription_id = db.Column(db.String(255), unique=True, index=True)
    
    # Subscription details
    tier = db.Column(db.String(50), default=SubscriptionTier.FREE, nullable=False)
    status = db.Column(db.String(50), default=SubscriptionStatus.FREE, nullable=False)
    
    # Billing period
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    
    # Cancellation
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    cancelled_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))

    def __repr__(self):
        return f'<Subscription user_id={self.user_id} tier={self.tier} status={self.status}>'

    def is_active(self):
        """Check if subscription is currently active."""
        if self.status == SubscriptionStatus.ACTIVE:
            if self.current_period_end and self.current_period_end > datetime.utcnow():
                return True
        return False

    def has_premium_access(self):
        """Check if user has premium access (any paid tier)."""
        return self.is_active() and self.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PRO]

    def to_dict(self):
        """Convert subscription to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier': self.tier,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'is_active': self.is_active(),
            'has_premium_access': self.has_premium_access(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }