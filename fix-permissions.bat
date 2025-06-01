@echo off
echo Fixing Cloud Run Secret Manager Permissions...

REM Set the project
gcloud config set project ttsai-461209

REM Grant Secret Manager Secret Accessor role to Cloud Run service account
echo Granting Secret Manager permissions to Cloud Run service account...
gcloud projects add-iam-policy-binding ttsai-461209 --member="serviceAccount:321805997355-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"

echo.
echo Checking if secrets exist...
gcloud secrets describe database-url
gcloud secrets describe redis-url
gcloud secrets describe asi-api-key
gcloud secrets describe jwt-secret
gcloud secrets describe encryption-key

echo.
echo Now redeploy with the updated cloudbuild.yaml:
echo gcloud builds submit --config=cloudbuild.yaml .

pause 