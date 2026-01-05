import express from 'express';
import jwt from 'jsonwebtoken';
import { body, validationResult } from 'express-validator';
import User from '../models/User.js';
import Organization from '../models/Organization.js';
import { auth } from '../middleware/auth.js';
import { generateSlug } from '../utils/helpers.js';

const router = express.Router();

// Validation rules
const registerValidation = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters'),
  body('firstName').trim().isLength({ min: 1 }).withMessage('First name is required'),
  body('lastName').trim().isLength({ min: 1 }).withMessage('Last name is required'),
  body('organizationName').trim().isLength({ min: 1 }).withMessage('Organization name is required'),
];

const loginValidation = [
  body('email').isEmail().normalizeEmail(),
  body('password').exists().withMessage('Password is required'),
];

// Generate JWT token
const generateToken = (userId, organizationId) => {
  return jwt.sign(
    { userId, organizationId },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
};

// @route   POST /api/auth/register
// @desc    Register new user and organization
// @access  Public
router.post('/register', registerValidation, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array(),
    });
  }

  const { email, password, firstName, lastName, organizationName, industry, companySize } = req.body;

  try {
    // Check if user already exists
    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User already exists with this email',
      });
    }

    // Create organization
    const orgSlug = await generateSlug(organizationName);
    const organization = new Organization({
      name: organizationName,
      slug: orgSlug,
      email,
      industry,
      companySize,
    });

    await organization.save();

    // Create user
    const user = new User({
      email,
      password,
      firstName,
      lastName,
      organizationId: organization._id,
      role: 'admin', // First user is admin
      isEmailVerified: true, // Auto-verify for now
    });

    await user.save();

    // Update organization usage
    organization.usage.users = 1;
    await organization.save();

    // Generate token
    const token = generateToken(user._id, organization._id);

    // Set HTTP-only cookie
    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.status(201).json({
      success: true,
      message: 'Registration successful',
      data: {
        user: {
          id: user._id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
        },
        organization: {
          id: organization._id,
          name: organization.name,
          slug: organization.slug,
          subscription: organization.subscription,
        },
      },
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      success: false,
      message: 'Registration failed',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

// @route   POST /api/auth/login
// @desc    Login user
// @access  Public
router.post('/login', loginValidation, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array(),
    });
  }

  const { email, password } = req.body;

  try {
    // Find user
    const user = await User.findByEmail(email).populate('organizationId');
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials',
      });
    }

    // Check password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials',
      });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Account is deactivated',
      });
    }

    // Check if organization is active
    if (!user.organizationId.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Organization is deactivated',
      });
    }

    // Update login stats
    user.lastLoginAt = new Date();
    user.loginCount += 1;
    await user.updateLastActive();

    // Generate token
    const token = generateToken(user._id, user.organizationId._id);

    // Set HTTP-only cookie
    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user._id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
        },
        organization: {
          id: user.organizationId._id,
          name: user.organizationId.name,
          slug: user.organizationId.slug,
          subscription: user.organizationId.subscription,
        },
      },
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Login failed',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

// @route   POST /api/auth/logout
// @desc    Logout user
// @access  Private
router.post('/logout', (req, res) => {
  res.clearCookie('token');
  res.json({
    success: true,
    message: 'Logout successful',
  });
});

// @route   GET /api/auth/me
// @desc    Get current user
// @access  Private
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId)
      .populate('organizationId')
      .select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found',
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          id: user._id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          preferences: user.preferences,
          lastLoginAt: user.lastLoginAt,
        },
        organization: {
          id: user.organizationId._id,
          name: user.organizationId.name,
          slug: user.organizationId.slug,
          subscription: user.organizationId.subscription,
          limits: user.organizationId.limits,
          usage: user.organizationId.usage,
        },
      },
    });

  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get user data',
    });
  }
});

// @route   POST /api/auth/refresh
// @desc    Refresh JWT token
// @access  Private
router.post('/refresh', auth, async (req, res) => {
  try {
    const token = generateToken(req.user.userId, req.user.organizationId);

    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.json({
      success: true,
      message: 'Token refreshed successfully',
    });

  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to refresh token',
    });
  }
});

export default router;