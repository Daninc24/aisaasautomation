#!/bin/bash

# AutomateIQ Health Check Script
echo "🏥 AutomateIQ Health Check"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Not in AutomateIQ root directory"
    exit 1
fi

echo "✅ In correct directory"

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not found"
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python not found"
fi

# Check AI engine virtual environment
if [ -d "ai-engine/venv" ]; then
    echo "✅ AI engine virtual environment exists"
    
    # Test AI engine imports
    cd ai-engine
    if source venv/bin/activate && CUDA_VISIBLE_DEVICES='' python -c "from app.main import app" 2>/dev/null; then
        echo "✅ AI engine imports successfully"
    else
        echo "⚠️  AI engine has import issues (may need dependencies)"
    fi
    cd ..
else
    echo "❌ AI engine virtual environment missing"
fi

# Check environment file
if [ -f ".env" ]; then
    echo "✅ Environment file exists"
else
    echo "⚠️  .env file missing (copy from .env.example)"
fi

# Check critical files
critical_files=("backend/package.json" "ai-engine/requirements.txt" "docker-compose.yml")
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Check if services are running
echo ""
echo "🌐 Service Status:"

# Backend
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend running on port 5000"
else
    echo "⚠️  Backend not running on port 5000"
fi

# AI Engine
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ AI Engine running on port 8000"
else
    echo "⚠️  AI Engine not running on port 8000"
fi

# Frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend running on port 5173"
else
    echo "⚠️  Frontend not running on port 5173"
fi

echo ""
echo "📋 Quick Start Commands:"
echo "- Setup everything: ./setup.sh"
echo "- Start with Docker: docker-compose up -d"
echo "- Start manually:"
echo "  - Frontend: npm run dev"
echo "  - Backend: npm run backend:dev"
echo "  - AI Engine: npm run ai:start"

echo ""
echo "🔗 Access URLs (when running):"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:5000"
echo "- AI Engine: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"