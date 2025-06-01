# Mental Wellness Coach - Simple GCP Deployment Script (gcloud CLI only)
# This script deploys the application to GCP using only gcloud commands

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production"
)

Write-Host "Mental Wellness Coach - Simple GCP Deployment" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Global variables
$global:AsiApiKey = ""
$global:JwtSecret = ""
$global:EncryptionKey = ""
$global:DatabasePassword = ""

# Check prerequisites
function Check-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: Google Cloud SDK not found. Please install it first." -ForegroundColor Red
        exit 1
    }
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: Docker not found. Please install Docker Desktop first." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Prerequisites check passed" -ForegroundColor Green
}

# Get user input for secrets
function Get-UserInput {
    Write-Host "Please provide the required configuration:" -ForegroundColor Yellow
    Write-Host "NOTE: You can use 'demo-key' for testing purposes (AI features won't work)" -ForegroundColor Cyan
    
    $apiKeyInput = Read-Host -Prompt "Enter your ASI:One API Key (or 'demo-key' for testing)"
    
    if ([string]::IsNullOrEmpty($apiKeyInput)) {
        Write-Host "ERROR: ASI:One API Key is required" -ForegroundColor Red
        exit 1
    }
    
    $global:AsiApiKey = $apiKeyInput
    
    # Generate secure secrets
    $global:JwtSecret = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))
    $global:EncryptionKey = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))
    $global:DatabasePassword = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString()))
    
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host "   Project ID: $ProjectId" -ForegroundColor White
    Write-Host "   Region: $Region" -ForegroundColor White
    Write-Host "   Environment: $Environment" -ForegroundColor White
    Write-Host "   Secrets: Generated automatically" -ForegroundColor White
}

# Setup GCP project and enable APIs
function Setup-GcpProject {
    Write-Host "Setting up GCP project..." -ForegroundColor Yellow
    
    # Set the project
    Write-Host "   Setting project to $ProjectId..." -ForegroundColor Gray
    gcloud config set project $ProjectId
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to set GCP project. Please check the project ID." -ForegroundColor Red
        exit 1
    }
    
    # Enable required APIs
    Write-Host "Enabling required APIs..." -ForegroundColor Yellow
    $apis = @(
        "run.googleapis.com",
        "sqladmin.googleapis.com",
        "redis.googleapis.com",
        "secretmanager.googleapis.com",
        "cloudbuild.googleapis.com",
        "monitoring.googleapis.com",
        "logging.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-Host "   Enabling $api..." -ForegroundColor Gray
        gcloud services enable $api --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Failed to enable $api, continuing..." -ForegroundColor Yellow
        }
    }
    
    Write-Host "GCP project setup completed" -ForegroundColor Green
}

# Create Cloud SQL database
function Create-Database {
    Write-Host "Creating Cloud SQL PostgreSQL database..." -ForegroundColor Yellow
    
    $instanceName = "wellness-postgres-$Environment"
    
    # Check if instance already exists
    $existingInstance = gcloud sql instances describe $instanceName 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Database instance already exists, skipping creation..." -ForegroundColor Gray
    } else {
        Write-Host "   Creating new database instance..." -ForegroundColor Gray
        gcloud sql instances create $instanceName `
            --database-version=POSTGRES_15 `
            --tier=db-f1-micro `
            --region=$Region `
            --storage-size=20GB `
            --storage-type=SSD `
            --backup-start-time=02:00 `
            --backup `
            --maintenance-window-day=SUN `
            --maintenance-window-hour=02 `
            --authorized-networks=0.0.0.0/0
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to create database instance" -ForegroundColor Red
            exit 1
        }
    }
    
    # Create database
    Write-Host "   Creating wellness_coach database..." -ForegroundColor Gray
    gcloud sql databases create wellness_coach --instance=$instanceName 2>$null
    
    # Create user
    Write-Host "   Creating database user..." -ForegroundColor Gray
    gcloud sql users create wellness_user --instance=$instanceName --password=$global:DatabasePassword 2>$null
    
    # Get connection name
    $connectionName = gcloud sql instances describe $instanceName --format="value(connectionName)"
    Write-Host "   Database connection name: $connectionName" -ForegroundColor Gray
    
    Write-Host "Database created successfully" -ForegroundColor Green
    return @{
        InstanceName = $instanceName
        ConnectionName = $connectionName
        DatabaseUrl = "postgresql://wellness_user:$($global:DatabasePassword)@/$instanceName/wellness_coach?host=/cloudsql/$connectionName"
    }
}

# Create Redis cache
function Create-Redis {
    Write-Host "Creating Redis cache..." -ForegroundColor Yellow
    
    $redisName = "wellness-redis-$Environment"
    
    # Check if Redis instance already exists
    $existingRedis = gcloud redis instances describe $redisName --region=$Region 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Redis instance already exists, skipping creation..." -ForegroundColor Gray
    } else {
        Write-Host "   Creating new Redis instance..." -ForegroundColor Gray
        gcloud redis instances create $redisName `
            --size=1 `
            --region=$Region `
            --redis-version=redis_6_x
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to create Redis instance" -ForegroundColor Red
            exit 1
        }
    }
    
    # Get Redis host and port
    $redisHost = gcloud redis instances describe $redisName --region=$Region --format="value(host)"
    $redisPort = gcloud redis instances describe $redisName --region=$Region --format="value(port)"
    
    Write-Host "   Redis host: ${redisHost}:${redisPort}" -ForegroundColor Gray
    Write-Host "Redis created successfully" -ForegroundColor Green
    
    return "redis://${redisHost}:${redisPort}"
}

# Store secrets in Secret Manager
function Store-Secrets {
    param($DatabaseUrl, $RedisUrl)
    
    Write-Host "Storing secrets in Secret Manager..." -ForegroundColor Yellow
    
    # Store database URL
    Write-Host "   Storing database URL..." -ForegroundColor Gray
    echo $DatabaseUrl | gcloud secrets create database-url --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $DatabaseUrl | gcloud secrets versions add database-url --data-file=-
    }
    
    # Store Redis URL
    Write-Host "   Storing Redis URL..." -ForegroundColor Gray
    echo $RedisUrl | gcloud secrets create redis-url --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $RedisUrl | gcloud secrets versions add redis-url --data-file=-
    }
    
    # Store ASI API key
    Write-Host "   Storing ASI API key..." -ForegroundColor Gray
    echo $global:AsiApiKey | gcloud secrets create asi-api-key --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $global:AsiApiKey | gcloud secrets versions add asi-api-key --data-file=-
    }
    
    # Store JWT secret
    Write-Host "   Storing JWT secret..." -ForegroundColor Gray
    echo $global:JwtSecret | gcloud secrets create jwt-secret --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $global:JwtSecret | gcloud secrets versions add jwt-secret --data-file=-
    }
    
    # Store encryption key
    Write-Host "   Storing encryption key..." -ForegroundColor Gray
    echo $global:EncryptionKey | gcloud secrets create encryption-key --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $global:EncryptionKey | gcloud secrets versions add encryption-key --data-file=-
    }
    
    Write-Host "Secrets stored successfully" -ForegroundColor Green
}

# Build and deploy with Cloud Build
function Build-Application {
    Write-Host "Building application with Cloud Build..." -ForegroundColor Yellow
    
    # Create a simple Cloud Build configuration
    $cloudbuildConfig = @"
steps:
# Build the container image
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'build'
  - '-t'
  - 'gcr.io/$ProjectId/wellness-backend:latest'
  - '-f'
  - 'backend/Dockerfile'
  - '.'

# Push the container image
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'push'
  - 'gcr.io/$ProjectId/wellness-backend:latest'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
"@
    
    # Write Cloud Build config to temp file
    $tempCloudBuild = Join-Path $env:TEMP "cloudbuild-simple.yml"
    Set-Content -Path $tempCloudBuild -Value $cloudbuildConfig -Encoding UTF8
    
    # Submit build
    Write-Host "   Submitting build to Cloud Build..." -ForegroundColor Gray
    gcloud builds submit --config=$tempCloudBuild .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cloud Build failed" -ForegroundColor Red
        exit 1
    }
    
    # Clean up temp file
    Remove-Item $tempCloudBuild -ErrorAction SilentlyContinue
    
    Write-Host "Application built successfully" -ForegroundColor Green
}

# Deploy to Cloud Run
function Deploy-CloudRun {
    param($DatabaseConnectionName)
    
    Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
    
    Write-Host "   Deploying wellness-backend service..." -ForegroundColor Gray
    gcloud run deploy wellness-backend `
        --image="gcr.io/$ProjectId/wellness-backend:latest" `
        --region=$Region `
        --platform=managed `
        --allow-unauthenticated `
        --set-cloudsql-instances=$DatabaseConnectionName `
        --memory=2Gi `
        --cpu=2 `
        --max-instances=10 `
        --min-instances=0 `
        --port=5000 `
        --timeout=300 `
        --concurrency=100 `
        --set-env-vars="FLASK_ENV=production" `
        --update-secrets="DATABASE_URL=database-url:latest,REDIS_URL=redis-url:latest,ASI_ONE_API_KEY=asi-api-key:latest,JWT_SECRET=jwt-secret:latest,ENCRYPTION_KEY=encryption-key:latest"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cloud Run deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Cloud Run deployment successful" -ForegroundColor Green
}

# Get deployment information
function Get-DeploymentInfo {
    Write-Host "Getting deployment information..." -ForegroundColor Yellow
    
    # Get Cloud Run service URL
    $serviceUrl = gcloud run services describe wellness-backend --region=$Region --format="value(status.url)" 2>$null
    
    Write-Host ""
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "Application URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host "Project ID: $ProjectId" -ForegroundColor White
    Write-Host "Region: $Region" -ForegroundColor White
    Write-Host "Environment: $Environment" -ForegroundColor White
    Write-Host ""
    Write-Host "Test the deployment:" -ForegroundColor Yellow
    Write-Host "   Health check: $serviceUrl/health" -ForegroundColor Gray
    Write-Host "   API docs: $serviceUrl/docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test the application endpoints" -ForegroundColor White
    Write-Host "2. Configure custom domain (optional)" -ForegroundColor White
    Write-Host "3. Set up monitoring and alerts" -ForegroundColor White
    Write-Host "4. Configure backup policies" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "   View logs: gcloud run services logs tail wellness-backend --region=$Region" -ForegroundColor Gray
    Write-Host "   Update service: gcloud run services update wellness-backend --region=$Region" -ForegroundColor Gray
    Write-Host "   Service info: gcloud run services describe wellness-backend --region=$Region" -ForegroundColor Gray
}

# Main execution
function Main {
    try {
        Check-Prerequisites
        Get-UserInput
        Setup-GcpProject
        
        $dbInfo = Create-Database
        $redisUrl = Create-Redis
        
        Store-Secrets -DatabaseUrl $dbInfo.DatabaseUrl -RedisUrl $redisUrl
        Build-Application
        Deploy-CloudRun -DatabaseConnectionName $dbInfo.ConnectionName
        Get-DeploymentInfo
        
        Write-Host ""
        Write-Host "All done! Your Mental Wellness Coach app is now live on Google Cloud!" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Check the logs above for specific error details." -ForegroundColor Yellow
        exit 1
    }
}

# Run the deployment
Main 