# Mental Wellness Coach - Cloud Deployment Guide

This guide provides comprehensive instructions for deploying the Mental Wellness Coach application to various cloud platforms.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [AWS Deployment](#aws-deployment)
- [Google Cloud Platform Deployment](#gcp-deployment)
- [Microsoft Azure Deployment](#azure-deployment)
- [Local Docker Deployment](#local-docker-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Tools

1. **Docker** (latest version)
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Cloud CLI Tools** (choose based on your platform):
   - **AWS CLI**: `pip install awscli`
   - **Google Cloud SDK**: [Installation Guide](https://cloud.google.com/sdk/docs/install)
   - **Azure CLI**: `pip install azure-cli`

3. **Terraform** (for infrastructure as code)
   ```bash
   # Install Terraform
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

### Required Accounts

- Cloud provider account (AWS, GCP, or Azure)
- ASI:One API account for LLM services
- Domain registrar account (optional, for custom domain)

## 🔑 Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Application Configuration
FLASK_ENV=production
APP_NAME=mental-wellness-coach
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/wellness_coach

# Redis Configuration
REDIS_URL=redis://host:6379

# AI Service Configuration
ASI_ONE_API_KEY=your_asi_api_key_here
ASI_ONE_API_BASE=https://api.asi1.ai/v1
ASI_ONE_MODEL=asi1-mini

# Security Configuration
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# Fetch.ai Configuration (for uAgents)
FETCH_AI_AGENT_KEY=your_fetch_ai_key_here

# Monitoring Configuration
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here (optional)
```

### Generate Secure Keys

```bash
# Generate JWT Secret (32 characters)
openssl rand -base64 32

# Generate Encryption Key (32 characters)
openssl rand -base64 32

# Generate Fetch.ai Agent Key (if needed)
python -c "import secrets; print(secrets.token_hex(32))"
```

## ☁️ AWS Deployment

### Step 1: Setup AWS CLI

```bash
# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Default region, and output format
```

### Step 2: Deploy Infrastructure

```bash
# Clone the repository
git clone https://github.com/your-org/mental-wellness-coach.git
cd mental-wellness-coach

# Navigate to deployment directory
cd deployment

# Extract AWS configuration files
kubectl apply -f aws-deployment.yml --dry-run=client -o yaml | grep -A 1000 "cloudformation-template.yml" | tail -n +2 > cloudformation-template.yml

# Deploy infrastructure
./deploy.sh
```

### Step 3: Configure Secrets

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret --name "wellness/asi-api-key" --secret-string "your_asi_api_key"
aws secretsmanager create-secret --name "wellness/jwt-secret" --secret-string "your_jwt_secret"
aws secretsmanager create-secret --name "wellness/encryption-key" --secret-string "your_encryption_key"
```

### Step 4: Deploy Application

```bash
# Build and push Docker image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t wellness-backend:latest -f backend/Dockerfile .

# Tag and push
docker tag wellness-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/wellness-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/wellness-backend:latest
```

### AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet Gateway                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                Application Load Balancer                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               ECS Fargate Service (2 tasks)                 │
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │  Wellness       │       │  Wellness       │              │
│  │  Backend        │       │  Backend        │              │
│  │  Container      │       │  Container      │              │
│  └─────────────────┘       └─────────────────┘              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                ┌─────────▼─────────┐
                │                   │
        ┌───────▼─────────┐  ┌─────▼─────────┐
        │  RDS PostgreSQL │  │ ElastiCache   │
        │   (Multi-AZ)    │  │    Redis      │
        └─────────────────┘  └───────────────┘
```

## 🌐 Google Cloud Platform Deployment

### Step 1: Setup GCP CLI

```bash
# Initialize gcloud
gcloud init

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com sqladmin.googleapis.com
```

### Step 2: Deploy with Terraform

```bash
# Extract GCP Terraform files
kubectl apply -f gcp-deployment.yml --dry-run=client -o yaml | grep -A 2000 "main.tf" | tail -n +2 > main.tf

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="project_id=YOUR_PROJECT_ID"

# Apply infrastructure
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

### Step 3: Build and Deploy Application

```bash
# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yml .

# Deploy to Cloud Run
gcloud run deploy wellness-backend \
  --image gcr.io/YOUR_PROJECT_ID/wellness-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

### GCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Load Balancer                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Cloud Run Service                        │
│         (Auto-scaling 0-10 instances)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                ┌─────────▼─────────┐
                │                   │
        ┌───────▼─────────┐  ┌─────▼─────────┐
        │   Cloud SQL     │  │ Memorystore   │
        │  PostgreSQL     │  │    Redis      │
        └─────────────────┘  └───────────────┘
```

## 🔷 Microsoft Azure Deployment

### Step 1: Setup Azure CLI

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription YOUR_SUBSCRIPTION_ID

# Create resource group
az group create --name mental-wellness-coach-rg --location eastus
```

### Step 2: Deploy Infrastructure

```bash
# Extract Azure ARM template
kubectl apply -f azure-deployment.yml --dry-run=client -o yaml | grep -A 3000 "azuredeploy.json" | tail -n +2 > azuredeploy.json

# Deploy with ARM template
az deployment group create \
  --resource-group mental-wellness-coach-rg \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json
```

### Step 3: Build and Deploy Application

```bash
# Create Azure Container Registry
az acr create --resource-group mental-wellness-coach-rg --name wellnessacr --sku Basic

# Build and push image
az acr build --registry wellnessacr --image wellness-backend:latest backend/
```

### Azure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Front Door                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                Container Instances                          │
│              (Auto-scaling group)                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                ┌─────────▼─────────┐
                │                   │
        ┌───────▼─────────┐  ┌─────▼─────────┐
        │  Azure Database │  │  Azure Cache  │
        │  for PostgreSQL │  │  for Redis    │
        └─────────────────┘  └───────────────┘
```

## 🐳 Local Docker Deployment

For local development and testing:

```bash
# Use the existing docker-compose setup
cd deployment
docker-compose -f docker-compose.yml up -d

# Or use the local development version
cd ..
npm run docker:up
```

## 📊 Monitoring and Maintenance

### Health Checks

All deployments include health check endpoints:

- **Application Health**: `GET /health`
- **Database Health**: `GET /health/db`
- **Redis Health**: `GET /health/redis`

### Monitoring Setup

1. **AWS**: CloudWatch + X-Ray
2. **GCP**: Cloud Monitoring + Cloud Trace
3. **Azure**: Application Insights + Azure Monitor

### Backup Strategy

1. **Database Backups**: Automated daily backups with 7-day retention
2. **Application Logs**: Centralized logging with 30-day retention
3. **Disaster Recovery**: Cross-region replication for production

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker run --rm postgres:15 pg_isready -h YOUR_DB_HOST -p 5432
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli -h YOUR_REDIS_HOST ping
   ```

3. **Container Startup Issues**
   ```bash
   # Check container logs
   docker logs <container_id>
   
   # For cloud deployments, check platform-specific logs
   # AWS: CloudWatch Logs
   # GCP: Cloud Logging
   # Azure: Container Insights
   ```

### Performance Optimization

1. **Database Optimization**
   - Enable connection pooling
   - Configure appropriate instance sizes
   - Monitor query performance

2. **Application Scaling**
   - Configure auto-scaling based on CPU/memory
   - Implement horizontal pod autoscaling
   - Use CDN for static assets

3. **Security Hardening**
   - Enable SSL/TLS everywhere
   - Use secret management services
   - Configure network security groups
   - Enable audit logging

## 📞 Support

For deployment issues:

1. Check the application logs first
2. Verify environment variables are correctly set
3. Ensure all required secrets are configured
4. Contact support with specific error messages and deployment platform

## 🔄 Updates and Maintenance

### Updating the Application

1. **AWS**: Update ECS task definition and service
2. **GCP**: Submit new Cloud Build or update Cloud Run service
3. **Azure**: Update container image in Container Instances

### Database Migrations

```bash
# Run database migrations
docker run --rm wellness-backend:latest flask db upgrade
```

### Security Updates

- Regularly update base Docker images
- Monitor for security vulnerabilities
- Apply security patches promptly
- Rotate secrets and API keys quarterly

---

**Note**: Replace placeholder values (YOUR_PROJECT_ID, YOUR_SUBSCRIPTION_ID, etc.) with your actual values before deployment. 