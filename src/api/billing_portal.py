from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import stripe
import os
from typing import Optional
from datetime import datetime

from src.database import get_db
from src.models.user import User
from src.auth.dependencies import get_current_user
from pydantic import BaseModel, HttpUrl

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/api/billing", tags=["billing"])


class BillingPortalResponse(BaseModel):
    url: HttpUrl


class PaymentHistoryItem(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    created: datetime
    description: Optional[str]
    invoice_pdf: Optional[str]


class PaymentHistoryResponse(BaseModel):
    payments: list[PaymentHistoryItem]
    has_more: bool


class SubscriptionDetails(BaseModel):
    subscription_id: Optional[str]
    status: Optional[str]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    plan_name: Optional[str]
    amount: Optional[int]
    currency: Optional[str]


@router.post("/portal", response_model=BillingPortalResponse)
async def create_billing_portal_session(
    return_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe billing portal session for the user to manage their subscription.
    Users can update payment methods, cancel subscriptions, and view invoices.
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Please subscribe first."
        )
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=return_url,
        )
        
        return BillingPortalResponse(url=portal_session.url)
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create billing portal session: {str(e)}"
        )


@router.get("/payment-history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    limit: int = 10,
    starting_after: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve payment history for the current user.
    Returns list of charges/invoices with pagination support.
    """
    if not current_user.stripe_customer_id:
        return PaymentHistoryResponse(payments=[], has_more=False)
    
    try:
        # Fetch charges for the customer
        charges = stripe.Charge.list(
            customer=current_user.stripe_customer_id,
            limit=limit,
            starting_after=starting_after
        )
        
        payment_items = []
        for charge in charges.data:
            payment_items.append(PaymentHistoryItem(
                id=charge.id,
                amount=charge.amount,
                currency=charge.currency,
                status=charge.status,
                created=datetime.fromtimestamp(charge.created),
                description=charge.description,
                invoice_pdf=charge.receipt_url
            ))
        
        return PaymentHistoryResponse(
            payments=payment_items,
            has_more=charges.has_more
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve payment history: {str(e)}"
        )


@router.get("/subscription", response_model=SubscriptionDetails)
async def get_subscription_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription details for the user.
    """
    if not current_user.stripe_subscription_id:
        return SubscriptionDetails(
            subscription_id=None,
            status=None,
            current_period_end=None,
            cancel_at_period_end=False,
            plan_name="Free",
            amount=None,
            currency=None
        )
    
    try:
        subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
        
        plan = subscription['items'].data[0].plan if subscription['items'].data else None
        
        return SubscriptionDetails(
            subscription_id=subscription.id,
            status=subscription.status,
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            cancel_at_period_end=subscription.cancel_at_period_end,
            plan_name=plan.nickname or plan.id if plan else None,
            amount=plan.amount if plan else None,
            currency=plan.currency if plan else None
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscription details: {str(e)}"
        )


@router.post("/subscription/cancel")
async def cancel_subscription(
    at_period_end: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel the user's subscription.
    If at_period_end is True, subscription remains active until end of billing period.
    """
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found."
        )
    
    try:
        if at_period_end:
            subscription = stripe.Subscription.modify(
                current_user.stripe_subscription_id,
                cancel_at_period_end=True
            )
        else:
            subscription = stripe.Subscription.delete(current_user.stripe_subscription_id)
            current_user.stripe_subscription_id = None
            current_user.subscription_tier = "free"
            db.commit()
        
        return {
            "message": "Subscription cancelled successfully",
            "cancel_at_period_end": subscription.cancel_at_period_end if at_period_end else False,
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end) if at_period_end else None
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )
