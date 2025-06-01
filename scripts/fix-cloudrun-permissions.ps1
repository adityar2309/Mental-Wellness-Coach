# Mental Wellness Coach - Fix Cloud Run Secret Manager Permissions
# This script fixes the deployment issue by granting proper permissions to the Cloud Run service account

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

Write-Host "🔧 Fixing Cloud Run Secret Manager Permissions" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check prerequisites
function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
    
    if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Google Cloud SDK not found. Please install it first." -ForegroundColor Red
        exit 1
    }
    
    # Set the project
    gcloud config set project $ProjectId
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to set project. Please check project ID." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
}

# Get project number
function Get-ProjectNumber {
    Write-Host "🔍 Getting project information..." -ForegroundColor Yellow
    
    $projectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to get project number" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   Project ID: $ProjectId" -ForegroundColor Gray
    Write-Host "   Project Number: $projectNumber" -ForegroundColor Gray
    Write-Host "   Region: $Region" -ForegroundColor Gray
    
    return $projectNumber
}

# Grant Secret Manager permissions to Cloud Run service account
function Grant-SecretManagerPermissions {
    param($ProjectNumber)
    
    Write-Host "🔐 Granting Secret Manager permissions..." -ForegroundColor Yellow
    
    $serviceAccount = "${ProjectNumber}-compute@developer.gserviceaccount.com"
    Write-Host "   Service Account: $serviceAccount" -ForegroundColor Gray
    
    # Grant Secret Manager Secret Accessor role
    Write-Host "   Granting roles/secretmanager.secretAccessor..." -ForegroundColor Gray
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$serviceAccount" `
        --role="roles/secretmanager.secretAccessor"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to grant Secret Manager permissions" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Secret Manager permissions granted successfully" -ForegroundColor Green
}

# Verify secrets exist
function Verify-Secrets {
    Write-Host "🔍 Verifying secrets exist..." -ForegroundColor Yellow
    
    $secrets = @("database-url", "redis-url", "asi-api-key", "jwt-secret", "encryption-key")
    
    foreach ($secret in $secrets) {
        Write-Host "   Checking secret: $secret" -ForegroundColor Gray
        $result = gcloud secrets describe $secret 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ⚠️  Secret '$secret' not found. You may need to create it." -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ Secret '$secret' exists" -ForegroundColor Green
        }
    }
}

# Update Cloud Build configuration
function Update-CloudBuildConfig {
    Write-Host "📝 Updating Cloud Build configuration..." -ForegroundColor Yellow
    
    $cloudBuildPath = "cloudbuild.yaml"
    
    # Check if file exists
    if (!(Test-Path $cloudBuildPath)) {
        Write-Host "❌ cloudbuild.yaml not found in current directory" -ForegroundColor Red
        exit 1
    }
    
    # Create backup
    Copy-Item $cloudBuildPath "${cloudBuildPath}.backup"
    Write-Host "   Created backup: ${cloudBuildPath}.backup" -ForegroundColor Gray
    
    # Create updated cloudbuild.yaml with secrets
    $newContent = @"
steps:
# Build the container image
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'build'
  - '-t'
  - 'gcr.io/`$PROJECT_ID/wellness-backend:`$COMMIT_SHA'
  - '-t'
  - 'gcr.io/`$PROJECT_ID/wellness-backend:latest'
  - '-f'
  - 'backend/Dockerfile'
  - '.'

# Push the container image to Container Registry
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'push'
  - 'gcr.io/`$PROJECT_ID/wellness-backend:`$COMMIT_SHA'

- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'push'
  - 'gcr.io/`$PROJECT_ID/wellness-backend:latest'

# Deploy to Cloud Run with secrets
- name: 'gcr.io/cloud-builders/gcloud'
  args:
  - 'run'
  - 'deploy'
  - 'wellness-backend'
  - '--image'
  - 'gcr.io/`$PROJECT_ID/wellness-backend:`$COMMIT_SHA'
  - '--region'
  - '$Region'
  - '--platform'
  - 'managed'
  - '--allow-unauthenticated'
  - '--memory'
  - '2Gi'
  - '--cpu'
  - '2'
  - '--max-instances'
  - '10'
  - '--min-instances'
  - '0'
  - '--port'
  - '5000'
  - '--timeout'
  - '300'
  - '--concurrency'
  - '100'
  - '--set-env-vars'
  - 'FLASK_ENV=production'
  - '--update-secrets'
  - 'DATABASE_URL=database-url:latest,REDIS_URL=redis-url:latest,ASI_ONE_API_KEY=asi-api-key:latest,JWT_SECRET=jwt-secret:latest,ENCRYPTION_KEY=encryption-key:latest'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
"@

    Set-Content -Path $cloudBuildPath -Value $newContent
    Write-Host "✅ Updated cloudbuild.yaml with secret configuration" -ForegroundColor Green
}

# Redeploy with proper configuration
function Redeploy-Service {
    Write-Host "🚀 Redeploying Cloud Run service..." -ForegroundColor Yellow
    
    Write-Host "   Building and deploying with updated configuration..." -ForegroundColor Gray
    gcloud builds submit --config=cloudbuild.yaml .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Deployment successful" -ForegroundColor Green
    
    # Get service URL
    $serviceUrl = gcloud run services describe wellness-backend --region=$Region --format="value(status.url)"
    Write-Host "🌐 Service URL: $serviceUrl" -ForegroundColor Cyan
}

# Main execution
Write-Host "Starting Cloud Run permissions fix for project: $ProjectId" -ForegroundColor Cyan

Check-Prerequisites
$projectNumber = Get-ProjectNumber
Grant-SecretManagerPermissions -ProjectNumber $projectNumber
Verify-Secrets
Update-CloudBuildConfig
Redeploy-Service

Write-Host ""
Write-Host "🎉 Cloud Run permissions fix completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If any secrets were missing, create them using:" -ForegroundColor White
Write-Host "   echo 'your-secret-value' | gcloud secrets create secret-name --data-file=-" -ForegroundColor Gray
Write-Host "2. Monitor the service at:" -ForegroundColor White
Write-Host "   gcloud run services describe wellness-backend --region=$Region" -ForegroundColor Gray 