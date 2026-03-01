import pytest
import stripe
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.services.stripe_service import StripeService
from src.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from src.models.user import User
from src.database import db


class TestStripePaymentFlow:
    """Comprehensive tests for Stripe payment flow and subscription lifecycle"""

    @pytest.fixture
    def stripe_service(self):
        return StripeService()

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id="user_123",
            email="test@example.com",
            stripe_customer_id=None
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.fixture
    def premium_tier(self, db_session):
        tier = SubscriptionTier(
            id="tier_premium",
            name="Premium",
            price=9.99,
            stripe_price_id="price_premium_monthly",
            features={"unlimited_games": True, "no_ads": True}
        )
        db_session.add(tier)
        db_session.commit()
        return tier

    # Successful Payment Tests
    @patch('stripe.checkout.Session.create')
    @patch('stripe.Customer.create')
    def test_create_checkout_session_success(self, mock_customer, mock_session, stripe_service, test_user, premium_tier):
        """Test successful checkout session creation"""
        mock_customer.return_value = Mock(id="cus_123")
        mock_session.return_value = Mock(
            id="cs_test_123",
            url="https://checkout.stripe.com/pay/cs_test_123"
        )

        result = stripe_service.create_checkout_session(
            user_id=test_user.id,
            tier_id=premium_tier.id,
            success_url="https://app.com/success",
            cancel_url="https://app.com/cancel"
        )

        assert result["session_id"] == "cs_test_123"
        assert result["url"] == "https://checkout.stripe.com/pay/cs_test_123"
        mock_customer.assert_called_once()
        mock_session.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    def test_successful_payment_webhook(self, mock_webhook, stripe_service, test_user, premium_tier, db_session):
        """Test handling successful payment webhook"""
        test_user.stripe_customer_id = "cus_123"
        db_session.commit()

        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "customer": "cus_123",
                    "subscription": "sub_123",
                    "metadata": {"user_id": test_user.id, "tier_id": premium_tier.id}
                }
            }
        }
        mock_webhook.return_value = mock_event

        stripe_service.handle_webhook(payload="{}", sig_header="test_sig")

        subscription = db_session.query(Subscription).filter_by(user_id=test_user.id).first()
        assert subscription is not None
        assert subscription.stripe_subscription_id == "sub_123"
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.tier_id == premium_tier.id

    # Failed Payment Tests
    @patch('stripe.checkout.Session.create')
    def test_checkout_session_creation_failure(self, mock_session, stripe_service, test_user, premium_tier):
        """Test handling of failed checkout session creation"""
        mock_session.side_effect = stripe.error.StripeError("Payment method declined")

        with pytest.raises(stripe.error.StripeError):
            stripe_service.create_checkout_session(
                user_id=test_user.id,
                tier_id=premium_tier.id,
                success_url="https://app.com/success",
                cancel_url="https://app.com/cancel"
            )

    @patch('stripe.Webhook.construct_event')
    def test_payment_failed_webhook(self, mock_webhook, stripe_service, test_user, db_session):
        """Test handling payment failure webhook"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()

        mock_event = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "subscription": "sub_123",
                    "attempt_count": 1
                }
            }
        }
        mock_webhook.return_value = mock_event

        stripe_service.handle_webhook(payload="{}", sig_header="test_sig")

        updated_sub = db_session.query(Subscription).filter_by(stripe_subscription_id="sub_123").first()
        assert updated_sub.status == SubscriptionStatus.PAST_DUE

    # Subscription Lifecycle Tests
    @patch('stripe.Webhook.construct_event')
    def test_subscription_renewal_success(self, mock_webhook, stripe_service, test_user, db_session):
        """Test successful subscription renewal"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() + timedelta(days=1)
        )
        db_session.add(subscription)
        db_session.commit()

        new_period_end = datetime.utcnow() + timedelta(days=30)
        mock_event = {
            "type": "invoice.paid",
            "data": {
                "object": {
                    "subscription": "sub_123",
                    "period_end": int(new_period_end.timestamp())
                }
            }
        }
        mock_webhook.return_value = mock_event

        stripe_service.handle_webhook(payload="{}", sig_header="test_sig")

        updated_sub = db_session.query(Subscription).filter_by(stripe_subscription_id="sub_123").first()
        assert updated_sub.status == SubscriptionStatus.ACTIVE
        assert updated_sub.current_period_end.date() == new_period_end.date()

    @patch('stripe.Subscription.modify')
    @patch('stripe.Webhook.construct_event')
    def test_subscription_cancellation(self, mock_webhook, mock_modify, stripe_service, test_user, db_session):
        """Test subscription cancellation"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()

        mock_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_123",
                    "status": "canceled"
                }
            }
        }
        mock_webhook.return_value = mock_event

        stripe_service.handle_webhook(payload="{}", sig_header="test_sig")

        updated_sub = db_session.query(Subscription).filter_by(stripe_subscription_id="sub_123").first()
        assert updated_sub.status == SubscriptionStatus.CANCELED

    @patch('stripe.Subscription.modify')
    def test_subscription_upgrade(self, mock_modify, stripe_service, test_user, premium_tier, db_session):
        """Test subscription tier upgrade"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.ACTIVE,
            tier_id="tier_basic"
        )
        db_session.add(subscription)
        db_session.commit()

        mock_modify.return_value = Mock(id="sub_123")

        stripe_service.upgrade_subscription(
            subscription_id=subscription.id,
            new_tier_id=premium_tier.id
        )

        updated_sub = db_session.query(Subscription).get(subscription.id)
        assert updated_sub.tier_id == premium_tier.id
        mock_modify.assert_called_once()

    @patch('stripe.Webhook.construct_event')
    def test_subscription_expired(self, mock_webhook, stripe_service, test_user, db_session):
        """Test subscription expiration after failed payments"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.PAST_DUE
        )
        db_session.add(subscription)
        db_session.commit()

        mock_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_123",
                    "status": "canceled",
                    "canceled_at": int(datetime.utcnow().timestamp())
                }
            }
        }
        mock_webhook.return_value = mock_event

        stripe_service.handle_webhook(payload="{}", sig_header="test_sig")

        updated_sub = db_session.query(Subscription).filter_by(stripe_subscription_id="sub_123").first()
        assert updated_sub.status == SubscriptionStatus.CANCELED

    @patch('stripe.Webhook.construct_event')
    def test_trial_period_ending(self, mock_webhook, stripe_service, test_user, db_session):
        """Test trial period ending notification"""
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatus.TRIALING,
            trial_end=datetime.utcnow() + timedelta(days=3)
        )
        db_session.add(subscription)
        db_session.commit()

        mock_event = {
            "type": "customer.subscription.trial_will_end",
            "data": {
                "object": {
                    "id": "sub_123",
                    "trial_end": int((datetime.utcnow() + timedelta(days=3)).timestamp())
                }
            }
        }
        mock_webhook.return_value = mock_event

        result = stripe_service.handle_webhook(payload="{}", sig_header="test_sig")
        assert result["notification_sent"] is True

    def test_webhook_signature_validation_failure(self, stripe_service):
        """Test webhook with invalid signature"""
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            mock_webhook.side_effect = stripe.error.SignatureVerificationError(
                "Invalid signature", "sig_header"
            )

            with pytest.raises(stripe.error.SignatureVerificationError):
                stripe_service.handle_webhook(payload="{}", sig_header="invalid_sig")