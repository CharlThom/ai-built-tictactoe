import os
import stripe
from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.subscription import Subscription, SubscriptionStatus
from src.models.user import User
from src.database import db
from src.utils.logger import logger

stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


@stripe_webhook_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events for payment and subscription lifecycle."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event['type']
    event_data = event['data']['object']

    try:
        if event_type == 'checkout.session.completed':
            handle_checkout_completed(event_data)
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(event_data)
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(event_data)
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(event_data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_cancelled(event_data)
        elif event_type == 'customer.subscription.trial_will_end':
            handle_trial_ending(event_data)
        else:
            logger.info(f"Unhandled event type: {event_type}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500


def handle_checkout_completed(session):
    """Handle successful checkout session completion."""
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    client_reference_id = session.get('client_reference_id')

    if not client_reference_id:
        logger.warning("No client_reference_id in checkout session")
        return

    user = User.query.filter_by(id=client_reference_id).first()
    if not user:
        logger.error(f"User not found: {client_reference_id}")
        return

    # Retrieve subscription details from Stripe
    stripe_subscription = stripe.Subscription.retrieve(subscription_id)
    
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    if not subscription:
        subscription = Subscription(user_id=user.id)
        db.session.add(subscription)

    subscription.stripe_customer_id = customer_id
    subscription.stripe_subscription_id = subscription_id
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.tier = get_tier_from_price_id(stripe_subscription['items']['data'][0]['price']['id'])
    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
    subscription.updated_at = datetime.utcnow()

    db.session.commit()
    logger.info(f"Checkout completed for user {user.id}, subscription {subscription_id}")


def handle_payment_succeeded(invoice):
    """Handle successful payment/renewal."""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not subscription:
        logger.error(f"Subscription not found: {subscription_id}")
        return

    stripe_subscription = stripe.Subscription.retrieve(subscription_id)
    
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
    subscription.updated_at = datetime.utcnow()

    db.session.commit()
    logger.info(f"Payment succeeded for subscription {subscription_id}")


def handle_payment_failed(invoice):
    """Handle failed payment."""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not subscription:
        logger.error(f"Subscription not found: {subscription_id}")
        return

    subscription.status = SubscriptionStatus.PAST_DUE
    subscription.updated_at = datetime.utcnow()

    db.session.commit()
    logger.warning(f"Payment failed for subscription {subscription_id}")


def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates (plan changes, etc.)."""
    subscription_id = stripe_subscription['id']
    
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not subscription:
        logger.error(f"Subscription not found: {subscription_id}")
        return

    subscription.status = map_stripe_status(stripe_subscription['status'])
    subscription.tier = get_tier_from_price_id(stripe_subscription['items']['data'][0]['price']['id'])
    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
    subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
    subscription.updated_at = datetime.utcnow()

    db.session.commit()
    logger.info(f"Subscription updated: {subscription_id}")


def handle_subscription_cancelled(stripe_subscription):
    """Handle subscription cancellation."""
    subscription_id = stripe_subscription['id']
    
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not subscription:
        logger.error(f"Subscription not found: {subscription_id}")
        return

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    subscription.updated_at = datetime.utcnow()

    db.session.commit()
    logger.info(f"Subscription cancelled: {subscription_id}")


def handle_trial_ending(stripe_subscription):
    """Handle trial period ending soon."""
    subscription_id = stripe_subscription['id']
    logger.info(f"Trial ending soon for subscription: {subscription_id}")
    # Could trigger email notification here


def map_stripe_status(stripe_status):
    """Map Stripe subscription status to internal status."""
    status_map = {
        'active': SubscriptionStatus.ACTIVE,
        'past_due': SubscriptionStatus.PAST_DUE,
        'canceled': SubscriptionStatus.CANCELLED,
        'incomplete': SubscriptionStatus.INCOMPLETE,
        'incomplete_expired': SubscriptionStatus.CANCELLED,
        'trialing': SubscriptionStatus.TRIALING,
        'unpaid': SubscriptionStatus.PAST_DUE
    }
    return status_map.get(stripe_status, SubscriptionStatus.CANCELLED)


def get_tier_from_price_id(price_id):
    """Map Stripe price ID to subscription tier."""
    price_tier_map = {
        os.getenv('STRIPE_PREMIUM_PRICE_ID'): 'premium',
        os.getenv('STRIPE_PRO_PRICE_ID'): 'pro'
    }
    return price_tier_map.get(price_id, 'free')