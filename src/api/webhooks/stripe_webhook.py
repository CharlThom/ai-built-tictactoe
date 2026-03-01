from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
import stripe
import os
from datetime import datetime

from src.database import get_db
from src.models.user import User
from src.models.payment_event import PaymentEvent

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events for subscription lifecycle management.
    Updates user subscription status based on payment events.
    """
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Log the event
    payment_event = PaymentEvent(
        event_id=event.id,
        event_type=event.type,
        created_at=datetime.fromtimestamp(event.created),
        data=event.data.object
    )
    db.add(payment_event)
    
    # Handle different event types
    if event.type == "customer.subscription.created":
        handle_subscription_created(event.data.object, db)
    
    elif event.type == "customer.subscription.updated":
        handle_subscription_updated(event.data.object, db)
    
    elif event.type == "customer.subscription.deleted":
        handle_subscription_deleted(event.data.object, db)
    
    elif event.type == "invoice.payment_succeeded":
        handle_payment_succeeded(event.data.object, db)
    
    elif event.type == "invoice.payment_failed":
        handle_payment_failed(event.data.object, db)
    
    db.commit()
    
    return {"status": "success"}


def handle_subscription_created(subscription, db: Session):
    """Handle new subscription creation."""
    customer_id = subscription.customer
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user:
        user.stripe_subscription_id = subscription.id
        user.subscription_status = subscription.status
        user.subscription_tier = get_tier_from_subscription(subscription)
        user.subscription_current_period_end = datetime.fromtimestamp(subscription.current_period_end)


def handle_subscription_updated(subscription, db: Session):
    """Handle subscription updates (plan changes, cancellations, etc.)."""
    customer_id = subscription.customer
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user:
        user.subscription_status = subscription.status
        user.subscription_tier = get_tier_from_subscription(subscription)
        user.subscription_current_period_end = datetime.fromtimestamp(subscription.current_period_end)
        
        # If subscription is cancelled or past_due, downgrade to free
        if subscription.status in ["canceled", "unpaid"]:
            user.subscription_tier = "free"
            user.stripe_subscription_id = None


def handle_subscription_deleted(subscription, db: Session):
    """Handle subscription deletion/cancellation."""
    customer_id = subscription.customer
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user:
        user.stripe_subscription_id = None
        user.subscription_status = "canceled"
        user.subscription_tier = "free"
        user.subscription_current_period_end = None


def handle_payment_succeeded(invoice, db: Session):
    """Handle successful payment."""
    customer_id = invoice.customer
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user and invoice.subscription:
        user.subscription_status = "active"
        user.last_payment_date = datetime.fromtimestamp(invoice.created)


def handle_payment_failed(invoice, db: Session):
    """Handle failed payment."""
    customer_id = invoice.customer
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    
    if user:
        user.subscription_status = "past_due"
        # Optionally send notification to user about failed payment


def get_tier_from_subscription(subscription) -> str:
    """Extract subscription tier from Stripe subscription object."""
    if not subscription.items.data:
        return "free"
    
    price_id = subscription.items.data[0].price.id
    
    # Map Stripe price IDs to tier names
    tier_mapping = {
        os.getenv("STRIPE_PREMIUM_PRICE_ID"): "premium",
        os.getenv("STRIPE_PRO_PRICE_ID"): "pro",
    }
    
    return tier_mapping.get(price_id, "free")
