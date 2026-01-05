# AutomateIQ Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd automateiq
```

### 2. Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend
npm install
npm run dev
```

#### Frontend Setup
```bash
npm install
npm run dev
```

#### AI Engine Setup
```bash
cd ai-engine
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

## 🏭 Production Deployment

### Option 1: Cloud Deployment (Recommended)

#### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
vercel --prod

# Environment variables to set in Vercel:
# - VITE_API_URL=https://your-backend-url.com
```

#### Backend (Fly.io)
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Create fly.toml
cat > fly.toml << EOF
app = "automateiq-backend"
primary_region = "iad"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
EOF

# Deploy
fly deploy
```

#### AI Engine (Fly.io)
```bash
# Create separate app for AI engine
cat > ai-fly.toml << EOF
app = "automateiq-ai-engine"
primary_region = "iad"

[build]
  dockerfile = "ai-engine/Dockerfile"

[env]
  ENVIRONMENT = "production"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [services.concurrency]
    hard_limit = 10
    soft_limit = 8
    type = "connections"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
EOF

# Deploy AI engine
fly deploy -c ai-fly.toml
```

#### Database (MongoDB Atlas)
1. Create MongoDB Atlas account
2. Create cluster
3. Get connection string
4. Update environment variables

#### Cache/Queue (Redis Cloud)
1. Create Redis Cloud account
2. Create database
3. Get connection string
4. Update environment variables

### Option 2: VPS Deployment

#### Server Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 100GB SSD
- **Recommended**: 8 CPU cores, 16GB RAM, 200GB SSD
- **OS**: Ubuntu 22.04 LTS

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. Application Deployment
```bash
# Clone repository
git clone <repository-url>
cd automateiq

# Copy and configure environment
cp .env.example .env
nano .env

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Nginx Configuration
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/automateiq

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # AI Engine
    location /ai {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/automateiq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Option 3: Kubernetes Deployment

#### 1. Kubernetes Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: automateiq

---
# k8s/mongodb.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: automateiq
spec:
  serviceName: mongodb
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: admin
        - name: MONGO_INITDB_ROOT_PASSWORD
          value: password123
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi

---
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: automateiq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379

---
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: automateiq
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: automateiq/backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: NODE_ENV
          value: production
        - name: MONGODB_URI
          value: mongodb://admin:password123@mongodb:27017/automateiq?authSource=admin
        - name: REDIS_URL
          value: redis://redis:6379

---
# k8s/ai-engine.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-engine
  namespace: automateiq
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-engine
  template:
    metadata:
      labels:
        app: ai-engine
    spec:
      containers:
      - name: ai-engine
        image: automateiq/ai-engine:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

---
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: automateiq
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017

---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: automateiq
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379

---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: automateiq
spec:
  selector:
    app: backend
  ports:
  - port: 5000
    targetPort: 5000

---
apiVersion: v1
kind: Service
metadata:
  name: ai-engine
  namespace: automateiq
spec:
  selector:
    app: ai-engine
  ports:
  - port: 8000
    targetPort: 8000

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: automateiq-ingress
  namespace: automateiq
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: automateiq-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 5000
      - path: /ai
        pathType: Prefix
        backend:
          service:
            name: ai-engine
            port:
              number: 8000
```

#### 2. Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n automateiq
kubectl get services -n automateiq
kubectl get ingress -n automateiq
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
NODE_ENV=production
PORT=5000
MONGODB_URI=mongodb://admin:password123@localhost:27017/automateiq?authSource=admin
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secret-jwt-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
FRONTEND_URL=https://your-frontend-domain.com
AI_ENGINE_URL=http://localhost:8000
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

#### AI Engine (.env)
```bash
ENVIRONMENT=production
REDIS_URL=redis://localhost:6379
MONGODB_URI=mongodb://admin:password123@localhost:27017/automateiq?authSource=admin
OPENAI_API_KEY=your-openai-api-key
```

#### Frontend (.env)
```bash
VITE_API_URL=https://your-backend-domain.com
VITE_APP_NAME=AutomateIQ
VITE_APP_VERSION=1.0.0
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://your-domain.com/api/health

# AI Engine health
curl https://your-domain.com/ai/health

# Database connection
docker exec -it automateiq-mongodb mongo --eval "db.adminCommand('ismaster')"
```

### Logs
```bash
# Docker Compose logs
docker-compose logs -f backend
docker-compose logs -f ai-engine

# Kubernetes logs
kubectl logs -f deployment/backend -n automateiq
kubectl logs -f deployment/ai-engine -n automateiq
```

### Backups
```bash
# MongoDB backup
docker exec automateiq-mongodb mongodump --out /backup --authenticationDatabase admin -u admin -p password123

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec automateiq-mongodb mongodump --out /backup/backup_$DATE --authenticationDatabase admin -u admin -p password123
tar -czf backup_$DATE.tar.gz /backup/backup_$DATE
aws s3 cp backup_$DATE.tar.gz s3://your-backup-bucket/
```

### Updates
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# For Kubernetes
kubectl set image deployment/backend backend=automateiq/backend:latest -n automateiq
kubectl set image deployment/ai-engine ai-engine=automateiq/ai-engine:latest -n automateiq
```

## 🔒 Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Set up monitoring alerts
- [ ] Review access permissions
- [ ] Enable 2FA for admin accounts
- [ ] Regular security updates

## 📈 Performance Optimization

### Database Optimization
```javascript
// MongoDB indexes
db.users.createIndex({ email: 1 })
db.users.createIndex({ organizationId: 1 })
db.documents.createIndex({ organizationId: 1, createdAt: -1 })
db.inventory.createIndex({ organizationId: 1, sku: 1 })
```

### Caching Strategy
```bash
# Redis configuration for production
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Load Balancing
```nginx
upstream backend {
    server backend1:5000;
    server backend2:5000;
    server backend3:5000;
}

upstream ai-engine {
    server ai-engine1:8000;
    server ai-engine2:8000;
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```bash
# Check MongoDB status
docker exec -it automateiq-mongodb mongo --eval "db.adminCommand('ismaster')"

# Check logs
docker logs automateiq-mongodb
```

#### 2. AI Engine Out of Memory
```bash
# Increase memory limits in docker-compose.yml
services:
  ai-engine:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 3. High CPU Usage
```bash
# Monitor processes
docker stats

# Scale services
docker-compose up -d --scale backend=3 --scale ai-engine=2
```

#### 4. SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

For additional support, check the logs and monitoring dashboards, or contact the development team.