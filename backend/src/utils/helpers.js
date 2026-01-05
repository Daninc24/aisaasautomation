import crypto from 'crypto';
import Organization from '../models/Organization.js';

/**
 * Generate a unique slug for organization
 */
export const generateSlug = async (name) => {
  const baseSlug = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim('-');

  let slug = baseSlug;
  let counter = 1;

  // Check if slug exists and increment if needed
  while (await Organization.findBySlug(slug)) {
    slug = `${baseSlug}-${counter}`;
    counter++;
  }

  return slug;
};

/**
 * Generate random token
 */
export const generateToken = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * Hash password using crypto
 */
export const hashPassword = (password) => {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
  return { salt, hash };
};

/**
 * Verify password
 */
export const verifyPassword = (password, salt, hash) => {
  const hashVerify = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
  return hash === hashVerify;
};

/**
 * Sanitize user input
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .substring(0, 1000); // Limit length
};

/**
 * Format error response
 */
export const formatError = (error, statusCode = 500) => {
  return {
    success: false,
    message: error.message || 'An error occurred',
    error: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    statusCode,
  };
};

/**
 * Format success response
 */
export const formatSuccess = (data, message = 'Success') => {
  return {
    success: true,
    message,
    data,
  };
};

/**
 * Validate email format
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Generate pagination metadata
 */
export const getPaginationMeta = (page, limit, total) => {
  const totalPages = Math.ceil(total / limit);
  const hasNextPage = page < totalPages;
  const hasPrevPage = page > 1;

  return {
    currentPage: page,
    totalPages,
    totalItems: total,
    itemsPerPage: limit,
    hasNextPage,
    hasPrevPage,
    nextPage: hasNextPage ? page + 1 : null,
    prevPage: hasPrevPage ? page - 1 : null,
  };
};

/**
 * Calculate AI credits cost based on operation
 */
export const calculateAICredits = (operation, complexity = 'medium') => {
  const baseCosts = {
    'document-ocr': { simple: 2, medium: 5, complex: 10 },
    'chat-message': { simple: 1, medium: 2, complex: 5 },
    'content-generation': { simple: 3, medium: 8, complex: 15 },
    'seo-analysis': { simple: 2, medium: 4, complex: 8 },
    'inventory-prediction': { simple: 5, medium: 10, complex: 20 },
    'report-generation': { simple: 3, medium: 7, complex: 12 },
  };

  return baseCosts[operation]?.[complexity] || 1;
};

/**
 * Check if file type is allowed
 */
export const isAllowedFileType = (mimetype, allowedTypes = []) => {
  const defaultAllowed = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ];

  const allowed = allowedTypes.length > 0 ? allowedTypes : defaultAllowed;
  return allowed.includes(mimetype);
};

/**
 * Generate file path for uploads
 */
export const generateFilePath = (organizationId, filename) => {
  const timestamp = Date.now();
  const randomString = crypto.randomBytes(8).toString('hex');
  const extension = filename.split('.').pop();
  
  return `${organizationId}/${timestamp}-${randomString}.${extension}`;
};

/**
 * Convert bytes to human readable format
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Delay execution (for rate limiting, etc.)
 */
export const delay = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Retry function with exponential backoff
 */
export const retryWithBackoff = async (fn, maxRetries = 3, baseDelay = 1000) => {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (i === maxRetries - 1) {
        throw lastError;
      }
      
      const delayTime = baseDelay * Math.pow(2, i);
      await delay(delayTime);
    }
  }
  
  throw lastError;
};