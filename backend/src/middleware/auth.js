import jwt from 'jsonwebtoken';
import User from '../models/User.js';
import Organization from '../models/Organization.js';

export const auth = async (req, res, next) => {
  try {
    // Get token from cookie or Authorization header
    let token = req.cookies.token;
    
    if (!token && req.headers.authorization) {
      const authHeader = req.headers.authorization;
      if (authHeader.startsWith('Bearer ')) {
        token = authHeader.substring(7);
      }
    }

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. No token provided.',
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Check if user exists and is active
    const user = await User.findById(decoded.userId).select('-password');
    if (!user || !user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token. User not found or inactive.',
      });
    }

    // Check if organization exists and is active
    const organization = await Organization.findById(decoded.organizationId);
    if (!organization || !organization.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token. Organization not found or inactive.',
      });
    }

    // Update last active time
    user.updateLastActive();

    // Attach user and organization to request
    req.user = {
      userId: user._id,
      organizationId: organization._id,
      role: user.role,
      email: user.email,
    };

    req.organization = organization;

    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token.',
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired.',
      });
    }

    console.error('Auth middleware error:', error);
    res.status(500).json({
      success: false,
      message: 'Authentication failed.',
    });
  }
};

// Role-based authorization middleware
export const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. Authentication required.',
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. Insufficient permissions.',
      });
    }

    next();
  };
};

// Check subscription status
export const checkSubscription = (requiredPlan = 'starter') => {
  const planHierarchy = {
    starter: 0,
    business: 1,
    enterprise: 2,
  };

  return (req, res, next) => {
    if (!req.organization) {
      return res.status(401).json({
        success: false,
        message: 'Organization context required.',
      });
    }

    const currentPlan = req.organization.subscription.plan;
    const subscriptionStatus = req.organization.subscription.status;

    // Check if subscription is active
    if (subscriptionStatus !== 'active') {
      return res.status(403).json({
        success: false,
        message: 'Subscription required. Please upgrade your plan.',
        code: 'SUBSCRIPTION_REQUIRED',
      });
    }

    // Check if current plan meets requirement
    if (planHierarchy[currentPlan] < planHierarchy[requiredPlan]) {
      return res.status(403).json({
        success: false,
        message: `${requiredPlan} plan or higher required.`,
        code: 'PLAN_UPGRADE_REQUIRED',
        requiredPlan,
        currentPlan,
      });
    }

    next();
  };
};

// Check AI credits
export const checkAICredits = (creditsRequired = 1) => {
  return (req, res, next) => {
    if (!req.organization) {
      return res.status(401).json({
        success: false,
        message: 'Organization context required.',
      });
    }

    if (!req.organization.canUseAICredits(creditsRequired)) {
      return res.status(403).json({
        success: false,
        message: 'Insufficient AI credits. Please upgrade your plan.',
        code: 'AI_CREDITS_EXHAUSTED',
        required: creditsRequired,
        available: req.organization.limits.aiCredits - req.organization.usage.aiCredits,
      });
    }

    next();
  };
};