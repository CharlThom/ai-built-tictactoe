from flask import Blueprint, request, jsonify
from functools import wraps
import os
from src.billing.stripe_service import StripeService

billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        # Add your JWT validation logic here
        request.user_id = auth_header.split(' ')[1]  # Simplified - use proper JWT decode
        return f(*args, **kwargs)
    return decorated_function


@billing_bp.route('/checkout/session', methods=['POST'])
@require_auth
def create_checkout_session():
    """Create a Stripe checkout session"""
    try:
        data = request.get_json()
        price_tier = data.get('tier')
        
        if not price_tier or price_tier not in ['basic', 'premium', 'pro']:
            return jsonify({'error': 'Invalid tier'}), 400
        
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        success_url = f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/billing/cancel"
        
        session = StripeService.create_checkout_session(
            user_id=request.user_id,
            price_tier=price_tier,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return jsonify(session), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@billing_bp.route('/portal/session', methods=['POST'])
@require_auth
def create_portal_session():
    """Create a customer portal session"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return_url = f"{base_url}/account/billing"
        
        session = StripeService.create_customer_portal_session(
            customer_id=customer_id,
            return_url=return_url
        )
        
        return jsonify(session), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@billing_bp.route('/subscription/<subscription_id>', methods=['GET'])
@require_auth
def get_subscription(subscription_id):
    """Get subscription details"""
    try:
        subscription = StripeService.get_subscription(subscription_id)
        return jsonify(subscription), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@billing_bp.route('/subscription/<subscription_id>/cancel', methods=['POST'])
@require_auth
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        data = request.get_json() or {}
        immediate = data.get('immediate', False)
        
        result = StripeService.cancel_subscription(subscription_id, immediate)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@billing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        event = StripeService.verify_webhook_signature(payload, sig_header)
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Update user subscription status in database
            user_id = session.get('client_reference_id')
            # TODO: Update database with subscription info
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            # TODO: Update subscription status in database
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            # TODO: Handle subscription cancellation
            
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            # TODO: Handle failed payment
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400