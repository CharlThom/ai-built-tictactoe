from functools import wraps
from flask import request, jsonify, g
from datetime import datetime
import os
from typing import Optional
import stripe
from src.models.user import User
from src.models.subscription import Subscription, SubscriptionTier

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class SubscriptionStatus:
    """Subscription status constants"""
    ACTIVE = 'active'
    CANCELED = 'canceled'
    PAST_DUE = 'past_due'
    TRIALING = 'trialing'
    INCOMPLETE = 'incomplete'
    INCOMPLETE_EXPIRED = 'incomplete_expired'
    UNPAID = 'unpaid'

class SubscriptionMiddleware:
    """Middleware for verifying user subscription status"""
    
    @staticmethod
    def get_user_subscription(user_id: int) -> Optional[Subscription]:
        """Retrieve active subscription for user"""
        return Subscription.query.filter_by(
            user_id=user_id,
            status=SubscriptionStatus.ACTIVE
        ).first()
    
    @staticmethod
    def sync_stripe_subscription(subscription: Subscription) -> Subscription:
        """Sync local subscription with Stripe status"""
        try:
            if subscription.stripe_subscription_id:
                stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                subscription.status = stripe_sub.status
                subscription.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
                subscription.save()
        except stripe.error.StripeError as e:
            print(f"Stripe sync error: {str(e)}")
        return subscription
    
    @staticmethod
    def has_premium_access(user_id: int) -> bool:
        """Check if user has active premium subscription"""
        subscription = SubscriptionMiddleware.get_user_subscription(user_id)
        
        if not subscription:
            return False
        
        # Sync with Stripe to ensure status is current
        subscription = SubscriptionMiddleware.sync_stripe_subscription(subscription)
        
        # Check if subscription is active and not expired
        if subscription.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            if subscription.current_period_end and subscription.current_period_end > datetime.utcnow():
                return subscription.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PREMIUM_PLUS]
        
        return False
    
    @staticmethod
    def check_game_limit(user_id: int) -> dict:
        """Check if user has reached game limit based on subscription tier"""
        from src.models.game import Game
        
        subscription = SubscriptionMiddleware.get_user_subscription(user_id)
        
        # Premium users have unlimited games
        if subscription and subscription.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PREMIUM_PLUS]:
            return {
                'allowed': True,
                'tier': subscription.tier,
                'games_remaining': -1  # Unlimited
            }
        
        # Free tier: limit to 10 games per day
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        games_today = Game.query.filter(
            Game.user_id == user_id,
            Game.created_at >= today_start
        ).count()
        
        free_tier_limit = 10
        games_remaining = max(0, free_tier_limit - games_today)
        
        return {
            'allowed': games_today < free_tier_limit,
            'tier': SubscriptionTier.FREE,
            'games_remaining': games_remaining,
            'limit': free_tier_limit
        }

def require_premium(f):
    """Decorator to require premium subscription for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user from request context (assumes auth middleware sets g.user)
        if not hasattr(g, 'user') or not g.user:
            return jsonify({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        user_id = g.user.id
        
        if not SubscriptionMiddleware.has_premium_access(user_id):
            return jsonify({
                'error': 'Premium subscription required',
                'code': 'PREMIUM_REQUIRED',
                'message': 'This feature requires an active premium subscription',
                'upgrade_url': '/api/subscriptions/checkout'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def check_game_limit_middleware(f):
    """Decorator to check game limits before allowing game creation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return jsonify({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        user_id = g.user.id
        limit_check = SubscriptionMiddleware.check_game_limit(user_id)
        
        if not limit_check['allowed']:
            return jsonify({
                'error': 'Game limit reached',
                'code': 'GAME_LIMIT_REACHED',
                'message': f"You have reached your daily limit of {limit_check['limit']} games",
                'tier': limit_check['tier'],
                'upgrade_url': '/api/subscriptions/checkout'
            }), 429
        
        # Store limit info in request context for use in endpoint
        g.game_limit_info = limit_check
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_subscription_tier(required_tier: str):
    """Decorator to require specific subscription tier"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            user_id = g.user.id
            subscription = SubscriptionMiddleware.get_user_subscription(user_id)
            
            if not subscription or subscription.tier != required_tier:
                return jsonify({
                    'error': f'{required_tier} subscription required',
                    'code': 'INSUFFICIENT_TIER',
                    'current_tier': subscription.tier if subscription else SubscriptionTier.FREE,
                    'required_tier': required_tier
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator