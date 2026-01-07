import express from 'express';
import { auth, authorize } from '../middleware/auth.js';
import { formatSuccess, formatError } from '../utils/helpers.js';

const router = express.Router();

// @route   GET /api/billing/plans
// @desc    Get pricing plans
// @access  Public
router.get('/plans', async (req, res) => {
  try {
    const plans = [
      {
        id: 'starter',
        name: 'Starter',
        price: 29,
        currency: 'USD',
        interval: 'month',
        features: [
          'Up to 5 users',
          '1,000 AI credits/month',
          'Basic automation',
          'Email support',
          '1GB storage'
        ],
        limits: {
          users: 5,
          aiCredits: 1000,
          storage: 1024,
          documents: 100
        }
      },
      {
        id: 'business',
        name: 'Business',
        price: 99,
        currency: 'USD',
        interval: 'month',
        popular: true,
        features: [
          'Up to 25 users',
          '10,000 AI credits/month',
          'Full automation suite',
          'Content creation tools',
          'Priority support',
          '10GB storage',
          'Advanced analytics'
        ],
        limits: {
          users: 25,
          aiCredits: 10000,
          storage: 10240,
          documents: 1000
        }
      },
      {
        id: 'enterprise',
        name: 'Enterprise',
        price: 299,
        currency: 'USD',
        interval: 'month',
        features: [
          'Unlimited users',
          '50,000 AI credits/month',
          'Custom integrations',
          'Dedicated AI models',
          '24/7 phone support',
          '100GB storage',
          'White-labeling',
          'API access'
        ],
        limits: {
          users: -1, // unlimited
          aiCredits: 50000,
          storage: 102400,
          documents: -1 // unlimited
        }
      }
    ];

    res.json(formatSuccess(plans));

  } catch (error) {
    console.error('Get plans error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   POST /api/billing/subscribe
// @desc    Subscribe to a plan
// @access  Private (Admin only)
router.post('/subscribe', auth, authorize('admin'), async (req, res) => {
  try {
    const { planId, paymentMethodId } = req.body;

    if (!planId || !paymentMethodId) {
      return res.status(400).json(formatError({ message: 'Plan ID and payment method are required' }, 400));
    }

    // TODO: Integrate with Stripe
    const subscription = {
      id: 'sub_' + Date.now(),
      planId,
      status: 'active',
      currentPeriodStart: new Date(),
      currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
      organizationId: req.user.organizationId
    };

    res.json(formatSuccess(subscription, 'Subscription created successfully'));

  } catch (error) {
    console.error('Subscribe error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   POST /api/billing/cancel
// @desc    Cancel subscription
// @access  Private (Admin only)
router.post('/cancel', auth, authorize('admin'), async (req, res) => {
  try {
    // TODO: Cancel Stripe subscription
    const result = {
      status: 'cancelled',
      cancelledAt: new Date(),
      effectiveDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // End of current period
    };

    res.json(formatSuccess(result, 'Subscription cancelled successfully'));

  } catch (error) {
    console.error('Cancel subscription error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   GET /api/billing/usage
// @desc    Get current usage statistics
// @access  Private
router.get('/usage', auth, async (req, res) => {
  try {
    // TODO: Get usage from organization
    const usage = {
      users: 1,
      aiCredits: 150,
      storage: 256,
      documents: 25,
      period: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date()
      }
    };

    res.json(formatSuccess(usage));

  } catch (error) {
    console.error('Get usage error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   GET /api/billing/invoices
// @desc    Get billing invoices
// @access  Private (Admin only)
router.get('/invoices', auth, authorize('admin'), async (req, res) => {
  try {
    // TODO: Get invoices from Stripe
    const invoices = [];

    res.json(formatSuccess(invoices));

  } catch (error) {
    console.error('Get invoices error:', error);
    res.status(500).json(formatError(error));
  }
});

export default router;