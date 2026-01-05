#!/bin/bash

# AutomateIQ Setup Script
# This script sets up the development environment for AutomateIQ

set -e  # Exit on any error

echo "🚀 Setting up AutomateIQ Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Ubuntu/Debian
if [[ -f /etc/debian_version ]]; then
    print_status "Detected Debian/Ubuntu system"
    
    # Install system dependencies
    print_status "Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3-full python3-pip python3-venv nodejs npm tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx libglib2.0-0
    
elif [[ -f /etc/redhat-release ]]; then
    print_status "Detected RedHat/CentOS system"
    
    # Install system dependencies for RHEL/CentOS
    sudo yum update -y
    sudo yum install -y python3 python3-pip python3-venv nodejs npm tesseract tesseract-langpack-eng
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew not found. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
    
    # Install system dependencies for macOS
    brew install python3 node tesseract
    
else
    print_warning "Unknown operating system. Please install dependencies manually:"
    print_warning "- Python 3.11+"
    print_warning "- Node.js 18+"
    print_warning "- Tesseract OCR"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. Installing Docker..."
    
    if [[ -f /etc/debian_version ]]; then
        # Install Docker on Ubuntu/Debian
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        print_success "Docker installed. Please log out and log back in to use Docker without sudo."
    else
        print_warning "Please install Docker manually: https://docs.docker.com/get-docker/"
    fi
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Installing..."
    
    if [[ -f /etc/debian_version ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed"
    else
        print_warning "Please install Docker Compose manually: https://docs.docker.com/compose/install/"
    fi
fi

# Setup environment file
print_status "Setting up environment configuration..."
if [[ ! -f .env ]]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file with your configuration before starting the services"
else
    print_warning ".env file already exists, skipping..."
fi

# Setup Frontend
print_status "Setting up Frontend (React)..."
if [[ -f package.json ]]; then
    npm install
    print_success "Frontend dependencies installed"
else
    print_error "package.json not found in root directory"
    exit 1
fi

# Setup Backend
print_status "Setting up Backend (Node.js)..."
if [[ -d backend && -f backend/package.json ]]; then
    cd backend
    npm install
    cd ..
    print_success "Backend dependencies installed"
else
    print_error "Backend directory or package.json not found"
    exit 1
fi

# Setup AI Engine
print_status "Setting up AI Engine (Python)..."
if [[ -d ai-engine && -f ai-engine/requirements.txt ]]; then
    cd ai-engine
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d venv ]]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Download spaCy model
    print_status "Downloading spaCy language model..."
    python -m spacy download en_core_web_sm
    
    deactivate
    cd ..
    print_success "AI Engine dependencies installed"
else
    print_error "AI Engine directory or requirements.txt not found"
    exit 1
fi

# Create uploads directory
print_status "Creating uploads directory..."
mkdir -p uploads
mkdir -p ai-engine/uploads
print_success "Upload directories created"

print_success "🎉 Setup completed successfully!"
echo ""
print_status "Next steps:"
echo "1. Edit .env file with your configuration (OpenAI API key, etc.)"
echo "2. Start the development environment:"
echo "   ${YELLOW}docker-compose up -d${NC}  (recommended)"
echo "   OR"
echo "   ${YELLOW}npm run dev${NC}  (manual setup)"
echo ""
print_status "Access the application:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:5000"
echo "- AI Engine: http://localhost:8000"
echo ""
print_status "For production deployment, see DEPLOYMENT.md"