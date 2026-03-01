import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import './Subscription.css';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY!);

interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  interval: 'month' | 'year';
  features: string[];
  stripePriceId: string;
  popular?: boolean;
}

const Subscription: React.FC = () => {
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentTier, setCurrentTier] = useState<string>('free');

  useEffect(() => {
    fetchSubscriptionTiers();
    fetchCurrentSubscription();
  }, []);

  const fetchSubscriptionTiers = async () => {
    try {
      const response = await fetch('/api/subscriptions/tiers', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch tiers');
      const data = await response.json();
      setTiers(data.tiers);
    } catch (err) {
      setError('Unable to load subscription plans');
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await fetch('/api/subscriptions/current', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentTier(data.tier || 'free');
      }
    } catch (err) {
      console.error('Failed to fetch current subscription');
    }
  };

  const handleSubscribe = async (stripePriceId: string, tierId: string) => {
    setLoading(tierId);
    setError(null);

    try {
      const response = await fetch('/api/subscriptions/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          priceId: stripePriceId,
          successUrl: `${window.location.origin}/subscription/success`,
          cancelUrl: `${window.location.origin}/subscription`
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create checkout session');
      }

      const { sessionId } = await response.json();
      const stripe = await stripePromise;
      
      if (!stripe) {
        throw new Error('Stripe failed to load');
      }

      const { error: stripeError } = await stripe.redirectToCheckout({ sessionId });
      
      if (stripeError) {
        throw new Error(stripeError.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(null);
    }
  };

  const handleManageSubscription = async () => {
    setLoading('manage');
    try {
      const response = await fetch('/api/subscriptions/create-portal-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          returnUrl: `${window.location.origin}/subscription`
        })
      });

      if (!response.ok) throw new Error('Failed to create portal session');
      
      const { url } = await response.json();
      window.location.href = url;
    } catch (err) {
      setError('Unable to open subscription management');
      setLoading(null);
    }
  };

  return (
    <div className="subscription-page">
      <div className="subscription-header">
        <h1>Choose Your Plan</h1>
        <p>Upgrade to premium for unlimited games and an ad-free experience</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="subscription-tiers">
        {tiers.map((tier) => (
          <div
            key={tier.id}
            className={`tier-card ${tier.popular ? 'popular' : ''} ${currentTier === tier.id ? 'current' : ''}`}
          >
            {tier.popular && <div className="popular-badge">Most Popular</div>}
            {currentTier === tier.id && <div className="current-badge">Current Plan</div>}
            
            <h2>{tier.name}</h2>
            <div className="price">
              <span className="amount">${tier.price}</span>
              <span className="interval">/{tier.interval}</span>
            </div>

            <ul className="features">
              {tier.features.map((feature, index) => (
                <li key={index}>
                  <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>

            {tier.id === 'free' ? (
              <button className="tier-button" disabled={currentTier === 'free'}>
                {currentTier === 'free' ? 'Current Plan' : 'Downgrade'}
              </button>
            ) : currentTier === tier.id ? (
              <button
                className="tier-button manage"
                onClick={handleManageSubscription}
                disabled={loading === 'manage'}
              >
                {loading === 'manage' ? 'Loading...' : 'Manage Subscription'}
              </button>
            ) : (
              <button
                className="tier-button subscribe"
                onClick={() => handleSubscribe(tier.stripePriceId, tier.id)}
                disabled={loading === tier.id}
              >
                {loading === tier.id ? 'Loading...' : currentTier === 'free' ? 'Subscribe' : 'Change Plan'}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="subscription-footer">
        <p>All plans include secure payment processing via Stripe</p>
        <p>Cancel anytime • No hidden fees • Instant activation</p>
      </div>
    </div>
  );
};

export default Subscription;