import pytest
import requests
import time
from datetime import datetime, timedelta
from src.app import create_app
from src.database import db
from src.models.user import User
from src.models.subscription import Subscription, SubscriptionStatus


class TestStripeEndToEnd:
    """End-to-end integration tests for Stripe payment flow"""

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        token = response.json['token']
        return {'Authorization': f'Bearer {token}'}

    def test_complete_subscription_flow(self, client, auth_headers):
        """Test complete flow: checkout -> payment -> activation -> usage"""
        # Step 1: Create checkout session
        response = client.post('/api/subscriptions/checkout', 
            headers=auth_headers,
            json={'tier': 'premium'}
        )
        assert response.status_code == 200
        session_data = response.json
        assert 'session_id' in session_data
        assert 'url' in session_data

        # Step 2: Simulate successful payment webhook
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': session_data['session_id'],
                    'customer': 'cus_test_123',
                    'subscription': 'sub_test_123',
                    'payment_status': 'paid'
                }
            }
        }
        response = client.post('/api/webhooks/stripe',
            json=webhook_payload,
            headers={'Stripe-Signature': 'test_signature'}
        )
        assert response.status_code == 200

        # Step 3: Verify subscription is active
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        assert response.status_code == 200
        subscription = response.json
        assert subscription['status'] == 'active'
        assert subscription['tier'] == 'premium'

        # Step 4: Verify premium features are accessible
        response = client.post('/api/games/create', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['ads_enabled'] is False

    def test_failed_payment_retry_flow(self, client, auth_headers):
        """Test payment failure and retry mechanism"""
        # Create active subscription
        client.post('/api/subscriptions/checkout', 
            headers=auth_headers,
            json={'tier': 'premium'}
        )

        # Simulate payment failure
        webhook_payload = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'subscription': 'sub_test_123',
                    'attempt_count': 1,
                    'next_payment_attempt': int((datetime.utcnow() + timedelta(days=3)).timestamp())
                }
            }
        }
        response = client.post('/api/webhooks/stripe', json=webhook_payload)
        assert response.status_code == 200

        # Verify subscription is past_due
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        assert response.json['status'] == 'past_due'

        # Simulate successful retry
        webhook_payload = {
            'type': 'invoice.paid',
            'data': {
                'object': {
                    'subscription': 'sub_test_123',
                    'attempt_count': 2
                }
            }
        }
        response = client.post('/api/webhooks/stripe', json=webhook_payload)
        assert response.status_code == 200

        # Verify subscription is active again
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        assert response.json['status'] == 'active'

    def test_subscription_cancellation_flow(self, client, auth_headers):
        """Test subscription cancellation and grace period"""
        # Create and activate subscription
        client.post('/api/subscriptions/checkout', 
            headers=auth_headers,
            json={'tier': 'premium'}
        )

        # Cancel subscription
        response = client.post('/api/subscriptions/cancel', headers=auth_headers)
        assert response.status_code == 200

        # Verify subscription is still active until period end
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        subscription = response.json
        assert subscription['cancel_at_period_end'] is True
        assert subscription['status'] == 'active'

        # Simulate period end webhook
        webhook_payload = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_test_123',
                    'status': 'canceled'
                }
            }
        }
        client.post('/api/webhooks/stripe', json=webhook_payload)

        # Verify subscription is now canceled
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        assert response.json['status'] == 'canceled'

    def test_subscription_upgrade_flow(self, client, auth_headers):
        """Test upgrading from basic to premium tier"""
        # Start with basic subscription
        client.post('/api/subscriptions/checkout', 
            headers=auth_headers,
            json={'tier': 'basic'}
        )

        # Upgrade to premium
        response = client.post('/api/subscriptions/upgrade',
            headers=auth_headers,
            json={'new_tier': 'premium'}
        )
        assert response.status_code == 200

        # Verify upgrade
        response = client.get('/api/subscriptions/current', headers=auth_headers)
        assert response.json['tier'] == 'premium'

    def test_webhook_idempotency(self, client):
        """Test that duplicate webhooks are handled idempotently"""
        webhook_payload = {
            'id': 'evt_unique_123',
            'type': 'invoice.paid',
            'data': {'object': {'subscription': 'sub_test_123'}}
        }

        # Send webhook twice
        response1 = client.post('/api/webhooks/stripe', json=webhook_payload)
        response2 = client.post('/api/webhooks/stripe', json=webhook_payload)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response2.json.get('already_processed') is True

    def test_subscription_status_transitions(self, client, auth_headers):
        """Test all valid subscription status transitions"""
        transitions = [
            ('trialing', 'active'),
            ('active', 'past_due'),
            ('past_due', 'active'),
            ('active', 'canceled'),
        ]

        for from_status, to_status in transitions:
            # Setup subscription in from_status
            response = client.get('/api/subscriptions/current', headers=auth_headers)
            
            # Trigger transition via webhook
            webhook_type = {
                'active': 'invoice.paid',
                'past_due': 'invoice.payment_failed',
                'canceled': 'customer.subscription.deleted'
            }.get(to_status, 'invoice.paid')

            webhook_payload = {
                'type': webhook_type,
                'data': {'object': {'subscription': 'sub_test_123', 'status': to_status}}
            }
            client.post('/api/webhooks/stripe', json=webhook_payload)

            # Verify transition
            response = client.get('/api/subscriptions/current', headers=auth_headers)
            assert response.json['status'] == to_status