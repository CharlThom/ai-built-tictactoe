import os
import stripe
from typing import Dict, Optional
from datetime import datetime

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


class StripeService:
    """Service for handling Stripe billing operations"""
    
    PRICE_IDS = {
        'basic': os.getenv('STRIPE_PRICE_BASIC'),
        'premium': os.getenv('STRIPE_PRICE_PREMIUM'),
        'pro': os.getenv('STRIPE_PRICE_PRO')
    }
    
    @staticmethod
    def create_checkout_session(
        user_id: str,
        price_tier: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """Create a Stripe checkout session for subscription"""
        try:
            price_id = StripeService.PRICE_IDS.get(price_tier)
            if not price_id:
                raise ValueError(f"Invalid price tier: {price_tier}")
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={'user_id': user_id, 'tier': price_tier},
                allow_promotion_codes=True,
                billing_address_collection='auto',
            )
            
            return {
                'session_id': session.id,
                'url': session.url,
                'status': 'created'
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_customer_portal_session(
        customer_id: str,
        return_url: str
    ) -> Dict:
        """Create a customer portal session for managing subscription"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            return {
                'url': session.url,
                'status': 'created'
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict]:
        """Retrieve subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'id': subscription.id,
                'customer_id': subscription.customer,
                'status': subscription.status,
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'items': [{
                    'price_id': item.price.id,
                    'product_id': item.price.product
                } for item in subscription['items']['data']]
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, immediate: bool = False) -> Dict:
        """Cancel a subscription"""
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'canceled': True
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str) -> Dict:
        """Verify Stripe webhook signature"""
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")