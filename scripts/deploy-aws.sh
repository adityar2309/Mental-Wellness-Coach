#!/bin/bash
set -e

# Mental Wellness Coach - AWS Deployment Script
# This script deploys the application to AWS ECS with all required infrastructure

echo "🚀 Mental Wellness Coach - AWS Deployment"
echo "=========================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first:"
        echo "   pip install awscli"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Get user input
get_input() {
    read -p "Enter AWS Region (default: us-east-1): " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    read -p "Enter Environment (default: production): " ENVIRONMENT
    ENVIRONMENT=${ENVIRONMENT:-production}
    
    read -p "Enter your ASI:One API Key: " -s ASI_API_KEY
    echo
    
    if [ -z "$ASI_API_KEY" ]; then
        echo "❌ ASI:One API Key is required"
        exit 1
    fi
    
    # Generate secure secrets
    JWT_SECRET=$(openssl rand -base64 32)
    ENCRYPTION_KEY=$(openssl rand -base64 32)
    
    echo "📝 Configuration:"
    echo "   Region: $AWS_REGION"
    echo "   Environment: $ENVIRONMENT"
    echo "   Secrets: Generated automatically"
}

# Extract deployment files from the ConfigMap
extract_files() {
    echo "📁 Extracting deployment configuration files..."
    
    # Extract CloudFormation template
    kubectl apply -f ../deployment/aws-deployment.yml --dry-run=client -o yaml | \
        grep -A 1000 "cloudformation-template.yml:" | \
        tail -n +2 | sed '/^[[:space:]]*[^[:space:]]/,$d' | \
        sed 's/^[[:space:]]*//' > cloudformation-template.yml
    
    # Extract task definition
    kubectl apply -f ../deployment/aws-deployment.yml --dry-run=client -o yaml | \
        grep -A 100 "task-definition.json:" | \
        tail -n +2 | sed '/^[[:space:]]*[^[:space:]]/,$d' | \
        sed 's/^[[:space:]]*//' > task-definition.json
    
    # Extract service definition
    kubectl apply -f ../deployment/aws-deployment.yml --dry-run=client -o yaml | \
        grep -A 50 "service-definition.json:" | \
        tail -n +2 | sed '/^[[:space:]]*[^[:space:]]/,$d' | \
        sed 's/^[[:space:]]*//' > service-definition.json
    
    echo "✅ Configuration files extracted"
}

# Create AWS resources
deploy_infrastructure() {
    echo "🏗️  Deploying AWS infrastructure..."
    
    # Get AWS Account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"
    
    # Create ECR repository
    echo "📦 Creating ECR repository..."
    aws ecr describe-repositories --repository-names wellness-backend --region $AWS_REGION &> /dev/null || \
        aws ecr create-repository --repository-name wellness-backend --region $AWS_REGION
    
    # Deploy CloudFormation stack
    echo "☁️  Deploying CloudFormation infrastructure..."
    aws cloudformation deploy \
        --template-file cloudformation-template.yml \
        --stack-name wellness-infrastructure-$ENVIRONMENT \
        --parameter-overrides Environment=$ENVIRONMENT \
        --capabilities CAPABILITY_IAM \
        --region $AWS_REGION
    
    echo "✅ Infrastructure deployed successfully"
}

# Store secrets
store_secrets() {
    echo "🔐 Storing secrets in AWS Secrets Manager..."
    
    aws secretsmanager create-secret \
        --name "wellness/asi-api-key" \
        --secret-string "$ASI_API_KEY" \
        --region $AWS_REGION &> /dev/null || \
    aws secretsmanager update-secret \
        --secret-id "wellness/asi-api-key" \
        --secret-string "$ASI_API_KEY" \
        --region $AWS_REGION
    
    aws secretsmanager create-secret \
        --name "wellness/jwt-secret" \
        --secret-string "$JWT_SECRET" \
        --region $AWS_REGION &> /dev/null || \
    aws secretsmanager update-secret \
        --secret-id "wellness/jwt-secret" \
        --secret-string "$JWT_SECRET" \
        --region $AWS_REGION
    
    aws secretsmanager create-secret \
        --name "wellness/encryption-key" \
        --secret-string "$ENCRYPTION_KEY" \
        --region $AWS_REGION &> /dev/null || \
    aws secretsmanager update-secret \
        --secret-id "wellness/encryption-key" \
        --secret-string "$ENCRYPTION_KEY" \
        --region $AWS_REGION
    
    echo "✅ Secrets stored successfully"
}

# Build and push Docker image
build_and_push() {
    echo "🐳 Building and pushing Docker image..."
    
    # Get ECR login
    aws ecr get-login-password --region $AWS_REGION | \
        docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build image
    echo "🔨 Building Docker image..."
    docker build -t wellness-backend:latest -f ../backend/Dockerfile ..
    
    # Tag and push
    echo "📤 Pushing to ECR..."
    docker tag wellness-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/wellness-backend:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/wellness-backend:latest
    
    echo "✅ Docker image built and pushed successfully"
}

# Deploy ECS service
deploy_service() {
    echo "🚀 Deploying ECS service..."
    
    # Update task definition with actual values
    sed -i.bak "s/ACCOUNT_ID/$AWS_ACCOUNT_ID/g" task-definition.json
    sed -i.bak "s/REGION/$AWS_REGION/g" task-definition.json
    
    # Register task definition
    echo "📋 Registering ECS task definition..."
    aws ecs register-task-definition \
        --cli-input-json file://task-definition.json \
        --region $AWS_REGION
    
    # Get CloudFormation outputs
    CLUSTER_NAME=$(aws cloudformation describe-stacks \
        --stack-name wellness-infrastructure-$ENVIRONMENT \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSCluster`].OutputValue' \
        --output text \
        --region $AWS_REGION)
    
    SUBNET_IDS=$(aws cloudformation describe-stacks \
        --stack-name wellness-infrastructure-$ENVIRONMENT \
        --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnets`].OutputValue' \
        --output text \
        --region $AWS_REGION)
    
    SECURITY_GROUP=$(aws cloudformation describe-stacks \
        --stack-name wellness-infrastructure-$ENVIRONMENT \
        --query 'Stacks[0].Outputs[?OutputKey==`BackendSecurityGroup`].OutputValue' \
        --output text \
        --region $AWS_REGION)
    
    # Update service definition
    sed -i.bak "s/\"subnet-12345\", \"subnet-67890\"/\"$(echo $SUBNET_IDS | tr ' ' ',')\"/g" service-definition.json
    sed -i.bak "s/sg-wellness-backend/$SECURITY_GROUP/g" service-definition.json
    sed -i.bak "s/wellness-cluster/$CLUSTER_NAME/g" service-definition.json
    
    # Create or update service
    echo "🔄 Creating ECS service..."
    aws ecs create-service \
        --cli-input-json file://service-definition.json \
        --region $AWS_REGION || \
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service wellness-backend-service \
        --task-definition wellness-backend \
        --region $AWS_REGION
    
    echo "✅ ECS service deployed successfully"
}

# Get deployment information
get_deployment_info() {
    echo "📊 Getting deployment information..."
    
    # Get Load Balancer DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name wellness-infrastructure-$ENVIRONMENT \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text \
        --region $AWS_REGION)
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "=================================="
    echo "📍 Application URL: http://$ALB_DNS"
    echo "🏗️  AWS Region: $AWS_REGION"
    echo "📋 Environment: $ENVIRONMENT"
    echo "🔗 CloudFormation Stack: wellness-infrastructure-$ENVIRONMENT"
    echo ""
    echo "📝 Next steps:"
    echo "1. Configure custom domain and SSL certificate"
    echo "2. Set up monitoring and alerts"
    echo "3. Configure backup policies"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: aws logs tail /ecs/wellness-backend --follow --region $AWS_REGION"
    echo "   Update service: aws ecs update-service --cluster $CLUSTER_NAME --service wellness-backend-service --force-new-deployment --region $AWS_REGION"
}

# Main execution
main() {
    check_prerequisites
    get_input
    extract_files
    deploy_infrastructure
    store_secrets
    build_and_push
    deploy_service
    get_deployment_info
}

# Create temporary directory for deployment files
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# Cleanup function
cleanup() {
    cd ..
    rm -rf $TEMP_DIR
}
trap cleanup EXIT

# Run deployment
main "$@" 