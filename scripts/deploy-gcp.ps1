# Mental Wellness Coach - Google Cloud Platform Deployment Script
# This script deploys the application to GCP using Cloud Run, Cloud SQL, and other GCP services

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production"
)

Write-Host "🚀 Mental Wellness Coach - GCP Deployment" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check prerequisites
function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
    
    if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Google Cloud SDK not found. Please install it first." -ForegroundColor Red
        exit 1
    }
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
        exit 1
    }
    
    if (!(Get-Command terraform -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Terraform not found. Please install Terraform first." -ForegroundColor Red
        Write-Host "   Download from: https://www.terraform.io/downloads.html" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
}

# Get user input for secrets
function Get-UserInput {
    Write-Host "🔑 Please provide the required API keys and secrets:" -ForegroundColor Yellow
    
    $global:AsiApiKey = Read-Host -Prompt "Enter your ASI:One API Key" -AsSecureString
    $global:AsiApiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($global:AsiApiKey))
    
    if ([string]::IsNullOrEmpty($global:AsiApiKeyPlain)) {
        Write-Host "❌ ASI:One API Key is required" -ForegroundColor Red
        exit 1
    }
    
    # Generate secure secrets
    $global:JwtSecret = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))
    $global:EncryptionKey = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))
    
    Write-Host "📝 Configuration:" -ForegroundColor Cyan
    Write-Host "   Project ID: $ProjectId" -ForegroundColor White
    Write-Host "   Region: $Region" -ForegroundColor White
    Write-Host "   Environment: $Environment" -ForegroundColor White
    Write-Host "   Secrets: Generated automatically" -ForegroundColor White
}

# Extract deployment files from ConfigMap
function Extract-Files {
    Write-Host "📁 Extracting deployment configuration files..." -ForegroundColor Yellow
    
    # Create temp directory for deployment files
    $tempDir = Join-Path $env:TEMP "gcp-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Set-Location $tempDir
    
    # Read the GCP deployment configuration
    $gcpConfig = Get-Content -Path "$(Split-Path $PSScriptRoot -Parent)\deployment\gcp-deployment.yml" -Raw
    
    # Extract Terraform main.tf
    $mainTfStart = $gcpConfig.IndexOf("main.tf: |")
    $mainTfEnd = $gcpConfig.IndexOf("`n  # Deployment Script", $mainTfStart)
    if ($mainTfEnd -eq -1) { $mainTfEnd = $gcpConfig.Length }
    
    $mainTfContent = $gcpConfig.Substring($mainTfStart, $mainTfEnd - $mainTfStart)
    $mainTfContent = $mainTfContent -replace "main\.tf: \|", ""
    $mainTfContent = ($mainTfContent -split "`n" | ForEach-Object { 
        if ($_ -match "^    (.*)") { $matches[1] } 
    }) -join "`n"
    
    Set-Content -Path "main.tf" -Value $mainTfContent -Encoding UTF8
    
    # Extract Cloud Build configuration
    $cloudbuildStart = $gcpConfig.IndexOf("cloudbuild.yml: |")
    $cloudbuildEnd = $gcpConfig.IndexOf("`n  # Terraform Infrastructure", $cloudbuildStart)
    if ($cloudbuildEnd -eq -1) { $cloudbuildEnd = $gcpConfig.Length }
    
    $cloudbuildContent = $gcpConfig.Substring($cloudbuildStart, $cloudbuildEnd - $cloudbuildStart)
    $cloudbuildContent = $cloudbuildContent -replace "cloudbuild\.yml: \|", ""
    $cloudbuildContent = ($cloudbuildContent -split "`n" | ForEach-Object { 
        if ($_ -match "^    (.*)") { $matches[1] } 
    }) -join "`n"
    
    Set-Content -Path "cloudbuild.yml" -Value $cloudbuildContent -Encoding UTF8
    
    Write-Host "✅ Configuration files extracted to: $tempDir" -ForegroundColor Green
    return $tempDir
}

# Setup GCP project
function Setup-GcpProject {
    Write-Host "🌐 Setting up GCP project..." -ForegroundColor Yellow
    
    # Set the project
    gcloud config set project $ProjectId
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to set GCP project. Please check the project ID." -ForegroundColor Red
        exit 1
    }
    
    # Enable required APIs
    Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow
    $apis = @(
        "run.googleapis.com",
        "sqladmin.googleapis.com", 
        "vpcaccess.googleapis.com",
        "redis.googleapis.com",
        "secretmanager.googleapis.com",
        "cloudbuild.googleapis.com",
        "monitoring.googleapis.com",
        "logging.googleapis.com",
        "compute.googleapis.com",
        "servicenetworking.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-Host "   Enabling $api..." -ForegroundColor Gray
        gcloud services enable $api --quiet
    }
    
    Write-Host "✅ GCP project setup completed" -ForegroundColor Green
}

# Create Terraform backend bucket
function Setup-TerraformBackend {
    Write-Host "🗄️  Setting up Terraform backend..." -ForegroundColor Yellow
    
    $bucketName = "$ProjectId-terraform-state"
    
    # Create bucket if it doesn't exist
    $bucketExists = gsutil ls -b "gs://$bucketName" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Creating Terraform state bucket..." -ForegroundColor Gray
        gsutil mb -p $ProjectId -l $Region "gs://$bucketName"
        gsutil versioning set on "gs://$bucketName"
    } else {
        Write-Host "   Terraform state bucket already exists" -ForegroundColor Gray
    }
    
    Write-Host "✅ Terraform backend ready" -ForegroundColor Green
}

# Deploy infrastructure with Terraform
function Deploy-Infrastructure {
    Write-Host "🏗️  Deploying infrastructure with Terraform..." -ForegroundColor Yellow
    
    # Initialize Terraform
    terraform init -backend-config="bucket=$ProjectId-terraform-state"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform initialization failed" -ForegroundColor Red
        exit 1
    }
    
    # Plan deployment
    Write-Host "📋 Planning Terraform deployment..." -ForegroundColor Gray
    terraform plan -var="project_id=$ProjectId" -var="environment=$Environment" -var="region=$Region"
    
    # Apply deployment
    Write-Host "🚀 Applying Terraform configuration..." -ForegroundColor Gray
    terraform apply -var="project_id=$ProjectId" -var="environment=$Environment" -var="region=$Region" -auto-approve
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Infrastructure deployed successfully" -ForegroundColor Green
}

# Store secrets in Secret Manager
function Store-Secrets {
    Write-Host "🔐 Storing secrets in Secret Manager..." -ForegroundColor Yellow
    
    # Store ASI API key
    Write-Host "   Storing ASI API key..." -ForegroundColor Gray
    echo $global:AsiApiKeyPlain | gcloud secrets create asi-api-key --data-file=- --replication-policy="automatic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        echo $global:AsiApiKeyPlain | gcloud secrets versions add asi-api-key --data-file=-
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
    
    Write-Host "✅ Secrets stored successfully" -ForegroundColor Green
}

# Build and deploy application
function Build-AndDeploy {
    Write-Host "🐳 Building and deploying application..." -ForegroundColor Yellow
    
    # Change back to project root
    $projectRoot = Split-Path $PSScriptRoot -Parent
    Set-Location $projectRoot
    
    # Submit build to Cloud Build
    Write-Host "🔨 Submitting build to Cloud Build..." -ForegroundColor Gray
    gcloud builds submit --config="$tempDir\cloudbuild.yml" --substitutions="_PROJECT_ID=$ProjectId,_REGION=$Region" .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Cloud Build submission failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Application built and deployed successfully" -ForegroundColor Green
}

# Get deployment information
function Get-DeploymentInfo {
    Write-Host "📊 Getting deployment information..." -ForegroundColor Yellow
    
    # Get Cloud Run service URL
    $serviceUrl = gcloud run services describe wellness-backend --region=$Region --format="value(status.url)" 2>$null
    
    Write-Host ""
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "📍 Application URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host "🌐 Project ID: $ProjectId" -ForegroundColor White
    Write-Host "📍 Region: $Region" -ForegroundColor White
    Write-Host "📋 Environment: $Environment" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Configure custom domain and SSL certificate" -ForegroundColor White
    Write-Host "2. Set up monitoring and alerting in Cloud Monitoring" -ForegroundColor White
    Write-Host "3. Configure backup policies" -ForegroundColor White
    Write-Host "4. Test the application endpoints" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Useful commands:" -ForegroundColor Yellow
    Write-Host "   View logs: gcloud run services logs tail wellness-backend --region=$Region" -ForegroundColor Gray
    Write-Host "   Update service: gcloud run services update wellness-backend --region=$Region" -ForegroundColor Gray
    Write-Host "   Monitor: gcloud run services describe wellness-backend --region=$Region" -ForegroundColor Gray
}

# Cleanup function
function Cleanup {
    if ($tempDir -and (Test-Path $tempDir)) {
        Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Main execution
function Main {
    try {
        Check-Prerequisites
        Get-UserInput
        $global:tempDir = Extract-Files
        Setup-GcpProject
        Setup-TerraformBackend
        Deploy-Infrastructure
        Store-Secrets
        Build-AndDeploy
        Get-DeploymentInfo
    }
    catch {
        Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    finally {
        Cleanup
    }
}

# Run the deployment
Main 