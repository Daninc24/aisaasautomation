import express from 'express';
import multer from 'multer';
import { auth, checkAICredits } from '../middleware/auth.js';
import { body, validationResult } from 'express-validator';
import { formatSuccess, formatError } from '../utils/helpers.js';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, process.env.UPLOAD_PATH || './uploads');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + '.' + file.originalname.split('.').pop());
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB default
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'), false);
    }
  }
});

// @route   POST /api/documents/upload
// @desc    Upload document for processing
// @access  Private
router.post('/upload', auth, checkAICredits(5), upload.single('document'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json(formatError({ message: 'No file uploaded' }, 400));
    }

    const { type = 'general' } = req.body;

    // TODO: Save document metadata to database
    const documentData = {
      filename: req.file.filename,
      originalName: req.file.originalname,
      mimetype: req.file.mimetype,
      size: req.file.size,
      path: req.file.path,
      type,
      organizationId: req.user.organizationId,
      uploadedBy: req.user.userId,
      status: 'uploaded',
      createdAt: new Date()
    };

    res.status(201).json(formatSuccess(documentData, 'Document uploaded successfully'));

  } catch (error) {
    console.error('Document upload error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   GET /api/documents
// @desc    Get documents list
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const { page = 1, limit = 10, type } = req.query;

    // TODO: Implement database query
    const documents = [];
    const total = 0;

    res.json(formatSuccess({
      documents,
      pagination: {
        currentPage: parseInt(page),
        totalPages: Math.ceil(total / limit),
        totalItems: total,
        itemsPerPage: parseInt(limit)
      }
    }));

  } catch (error) {
    console.error('Get documents error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   GET /api/documents/:id
// @desc    Get document details
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;

    // TODO: Implement database query
    const document = null;

    if (!document) {
      return res.status(404).json(formatError({ message: 'Document not found' }, 404));
    }

    res.json(formatSuccess(document));

  } catch (error) {
    console.error('Get document error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   POST /api/documents/process
// @desc    Process document with AI
// @access  Private
router.post('/process', auth, checkAICredits(10), [
  body('documentId').notEmpty().withMessage('Document ID is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json(formatError({ message: 'Validation failed', errors: errors.array() }, 400));
    }

    const { documentId } = req.body;

    // TODO: Send to AI engine for processing
    const processedData = {
      documentId,
      status: 'processing',
      message: 'Document processing started'
    };

    res.json(formatSuccess(processedData, 'Document processing started'));

  } catch (error) {
    console.error('Document processing error:', error);
    res.status(500).json(formatError(error));
  }
});

// @route   DELETE /api/documents/:id
// @desc    Delete document
// @access  Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;

    // TODO: Implement document deletion
    res.json(formatSuccess(null, 'Document deleted successfully'));

  } catch (error) {
    console.error('Delete document error:', error);
    res.status(500).json(formatError(error));
  }
});

export default router;