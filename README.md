# AutomateIQ - AI-Powered Business Automation & Content Intelligence SaaS

## 🎯 Product Overview
AutomateIQ is a unified AI-powered workflow automation and content optimization SaaS platform designed for SMBs, offering cost-efficient alternatives to enterprise software with automation-first workflows and AI at the core.

## 🏗️ System Architecture

### Frontend (React + Vite)
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS + ShadCN/Radix UI
- **State Management**: React Query + Zustand
- **Charts**: Recharts
- **Animation**: Framer Motion

### Backend Services
- **API Gateway**: Node.js + Express
- **Database**: MongoDB (multi-tenant)
- **Cache/Queue**: Redis
- **AI Engine**: Python microservices
- **Authentication**: JWT with HttpOnly cookies

### AI/ML Stack (Python)
- **OCR**: Tesseract + EasyOCR
- **NLP**: spaCy + Transformers
- **LLM**: OpenAI API + local fallbacks
- **ML**: scikit-learn + Prophet
- **Jobs**: Celery + Redis

### Infrastructure
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Proxy**: Nginx
- **Deployment**: Vercel (frontend) + Fly.io (backend)

## 🧩 Core Modules

### Module A: AI Workflow Automation
- Smart Document Processing (OCR + NLP)
- Automated Customer Support Triage
- Predictive Inventory Management
- Automated Report Generation

### Module B: AI Content Creation & Optimization
- AI Content Idea Generator
- Smart Content Generation
- SEO Optimization Engine
- Performance Analytics & Prediction
- Basic Visual Content Generation

## 💰 Pricing Strategy
- **Starter**: $29/month - Limited AI usage, basic automation
- **Business**: $99/month - Full automation, content suite, inventory prediction
- **Enterprise**: $299/month - Custom integrations, dedicated models, priority support

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (recommended)
- Git

### Option 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd automateiq

# Run setup script (handles everything automatically)
chmod +x setup.sh
./setup.sh

# Edit environment variables
nano .env

# Start with Docker
docker-compose up -d
```

### Option 2: Manual Setup

#### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd automateiq
cp .env.example .env
# Edit .env with your configuration
```

#### 2. Frontend Setup
```bash
npm install
```

#### 3. Backend Setup
```bash
cd backend
npm install
cd ..
```

#### 4. AI Engine Setup (Python Virtual Environment)
```bash
cd ai-engine

# Create virtual environment (Ubuntu/Debian)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Deactivate virtual environment
deactivate

cd ..
```

#### 5. Start Services

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual Start**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd backend
npm run dev

# Terminal 3: AI Engine
cd ai-engine
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 🌐 Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **AI Engine**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Environment Configuration

### Required Environment Variables
Create a `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values (NEVER commit .env to git)
nano .env
```

**⚠️ SECURITY WARNING**: Never commit `.env` files or any files containing secrets to version control. The `.gitignore` file is configured to prevent this, but always double-check before committing.

### Critical Secrets to Configure
```bash
# Generate a secure JWT secret (minimum 32 characters)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Database connection (use strong passwords)
MONGODB_URI=mongodb://admin:password123@localhost:27017/automateiq?authSource=admin

# OpenAI API key (required for AI features)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Other required secrets
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
SMTP_PASS=your-app-password
```

For detailed security guidelines, see [SECURITY.md](SECURITY.md).

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose build

# View running containers
docker-compose ps
```

## 🧪 Testing the Setup

### Health Checks
```bash
# Backend health
curl http://localhost:5000/health

# AI Engine health
curl http://localhost:8000/health
```

### Test API Endpoints
```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "firstName": "Test",
    "lastName": "User",
    "organizationName": "Test Company"
  }'
```

## 🔧 Development Scripts

```bash
# Frontend development
npm run dev                 # Start frontend dev server
npm run build              # Build for production
npm run preview            # Preview production build

# Backend development
npm run backend:dev        # Start backend dev server
npm run backend:install    # Install backend dependencies

# AI Engine development
npm run ai:install         # Install AI engine dependencies (calls setup script)

# Docker operations
npm run docker:up          # Start Docker services
npm run docker:down        # Stop Docker services
npm run docker:logs        # View Docker logs
```

## 📚 Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Security Guidelines](SECURITY.md)** - Security best practices and secret management
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🛠️ Troubleshooting

### Common Issues

#### Python Virtual Environment Issues (Ubuntu/Debian)
If you get "externally-managed-environment" error:
```bash
# Use virtual environment (recommended)
cd ai-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or run the setup script
./setup.sh
```

#### Docker Issues
```bash
# Check Docker status
docker --version
docker-compose --version

# Restart Docker services
docker-compose down
docker-compose up -d
```

#### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "5001:5000"  # Change from 5000 to 5001
```

#### MongoDB Connection Issues
```bash
# Check MongoDB container
docker-compose logs mongodb

# Reset MongoDB data
docker-compose down -v
docker-compose up -d
```

## 🚀 Production Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick production setup:
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Fly.io or Railway
- **Database**: MongoDB Atlas
- **Cache**: Redis Cloud

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check the docs folder
- **Issues**: Create a GitHub issue
- **Email**: support@automateiq.com