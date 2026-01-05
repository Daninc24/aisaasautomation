# AutomateIQ Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd automateiq
```

### Step 2: Run the Setup Script
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install system dependencies (Python, Node.js, Docker, etc.)
- Set up Python virtual environment for AI engine
- Install all project dependencies
- Create environment configuration file
- Download required AI models

### Step 3: Configure Environment
```bash
# Edit the environment file with your settings
nano .env
```

**Required settings:**
```bash
# Add your OpenAI API key for AI features
OPENAI_API_KEY=your-openai-api-key-here

# Other settings are pre-configured for development
```

### Step 4: Start the Application

**Option A: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual Start**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend  
npm run backend:dev

# Terminal 3: AI Engine
npm run ai:start
```

### Step 5: Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000/health
- **AI Engine**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## 🧪 Test Your Setup

### 1. Check Health Endpoints
```bash
# Backend health check
curl http://localhost:5000/health

# AI Engine health check  
curl http://localhost:8000/health
```

### 2. Register a Test User
```bash
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

### 3. Access the Frontend
Open http://localhost:5173 in your browser and you should see the AutomateIQ landing page.

## 🛠️ Troubleshooting

### Python Virtual Environment Issues (Ubuntu/Debian)
If you get "externally-managed-environment" error:
```bash
# The setup script handles this automatically, but if needed:
cd ai-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Docker Issues
```bash
# Check if Docker is running
docker --version
docker-compose --version

# If Docker isn't installed, the setup script will install it
# You may need to log out and back in after installation
```

### Port Conflicts
If you get port already in use errors:
```bash
# Check what's using the ports
sudo lsof -i :5000  # Backend
sudo lsof -i :5173  # Frontend  
sudo lsof -i :8000  # AI Engine

# Kill processes or change ports in docker-compose.yml
```

### Missing Dependencies
```bash
# Re-run the setup script
./setup.sh

# Or install manually:
npm install
cd backend && npm install
cd ../ai-engine && source venv/bin/activate && pip install -r requirements.txt
```

## 📋 What's Included

### Frontend Features
- Modern React 18 + Vite setup
- Tailwind CSS + ShadCN UI components
- Authentication system
- Responsive design
- Landing page with pricing

### Backend Features  
- Node.js + Express API
- MongoDB integration
- Redis caching
- JWT authentication
- Multi-tenant architecture
- Rate limiting & security

### AI Engine Features
- FastAPI Python service
- OCR document processing
- NLP text analysis
- Content generation
- Machine learning models
- Background job processing

## 🎯 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Customize the Frontend**: Modify components in `src/components/`
3. **Add AI Features**: Implement new AI services in `ai-engine/app/services/`
4. **Deploy to Production**: Follow the [Deployment Guide](DEPLOYMENT.md)

## 🆘 Need Help?

- **Documentation**: Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system info
- **Issues**: Create a GitHub issue
- **Setup Problems**: Re-run `./setup.sh` or check the troubleshooting section above

Happy coding! 🚀