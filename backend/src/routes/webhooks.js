import express from 'express';
import { formatSuccess, formatError } from '../utils/helpers.js';

const router = express.Router();

// @route   POST /api/webhooks/stripe
// @desc    Handle Stripe webhooks
// @access  Public (but verified)
router.post('/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

    if (!sig || !endpointSecret) {
      return res.status(400).json(formatError({ message: 'Missing signature or secret' }, 400));
    }

    // TODO: Verify Stripe webhook signature
    // const event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);

    // Mock event for now
    const event = {
      type: 'invoice.payment_succeeded',
      data: {
        object: {
          id: 'in_test',
          customer: 'cus_test',
          subscription: 'sub_test'
        }
      }
    };

    // Handle different event types
    switch (event.type) {
      case 'invoice.payment_succeeded':
        console.log('Payment succeeded:', event.data.object);
        // TODO: Update subscription status in database
        break;

      case 'invoice.payment_failed':
        console.log('Payment failed:', event.data.object);
        // TODO: Handle failed payment
        break;

      case 'customer.subscription.deleted':
        console.log('Subscription deleted:', event.data.object);
        // TODO: Deactivate subscription
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    res.json(formatSuccess({ received: true }));

  } catch (error) {
    console.error('Stripe webhook error:', error);
    res.status(400).json(formatError(error, 400));
  }
});

// @route   POST /api/webhooks/ai-engine
// @desc    Handle AI engine webhooks
// @access  Internal
router.post('/ai-engine', async (req, res) => {
  try {
    const { type, data } = req.body;

    switch (type) {
      case 'document.processed':
        console.log('Document processed:', data);
        // TODO: Update document status in database
        break;

      case 'report.generated':
        console.log('Report generated:', data);
        // TODO: Update report status and save results
        break;

      case 'prediction.completed':
        console.log('Prediction completed:', data);
        // TODO: Save prediction results
        break;

      default:
        console.log(`Unhandled AI engine event: ${type}`);
    }

    res.json(formatSuccess({ received: true }));

  } catch (error) {
    console.error('AI engine webhook error:', error);
    res.status(500).json(formatError(error));
  }
});

export default router;