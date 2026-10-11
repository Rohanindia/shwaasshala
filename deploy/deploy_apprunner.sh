#!/usr/bin/env bash
# Deploy ShwaasShala to AWS App Runner using AWS CLI
set -euo pipefail

APP_NAME="shwaasshala"
AWS_REGION="${AWS_REGION:-us-east-1}"
IMAGE_TAG="latest"

echo "=== 1. Checking AWS Account Identity ==="
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"

echo "Deploying ${APP_NAME} to AWS Region: ${AWS_REGION} (Account: ${AWS_ACCOUNT_ID})"

echo "=== 2. Creating ECR Repository if needed ==="
aws ecr describe-repositories --repository-names "${APP_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1 || \
aws ecr create-repository --repository-name "${APP_NAME}" --region "${AWS_REGION}"

echo "=== 3. Authenticating Docker to AWS ECR ==="
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "=== 4. Building and Pushing Docker Image ==="
docker build -t "${APP_NAME}:${IMAGE_TAG}" .
docker tag "${APP_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
docker push "${ECR_URI}:${IMAGE_TAG}"

echo "=== 5. Creating or Updating AWS App Runner Service ==="
cat <<EOF > /tmp/apprunner-config.json
{
  "ImageRepository": {
    "ImageIdentifier": "${ECR_URI}:${IMAGE_TAG}",
    "ImageConfiguration": {
      "Port": "8000",
      "RuntimeEnvironmentVariables": {
        "MODEL_PROVIDER": "bedrock",
        "AWS_REGION": "${AWS_REGION}",
        "ENVIRONMENT": "production"
      }
    },
    "ImageRepositoryType": "ECR"
  },
  "AutoDeploymentsEnabled": true
}
EOF

SERVICE_ARN=$(aws apprunner list-services --region "${AWS_REGION}" --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceArn" --output text)

if [ -z "${SERVICE_ARN}" ]; then
  echo "Creating new App Runner service..."
  aws apprunner create-service \
    --service-name "${APP_NAME}" \
    --source-configuration file:///tmp/apprunner-config.json \
    --instance-configuration Cpu=1024,Memory=2048 \
    --region "${AWS_REGION}"
else
  echo "Updating existing App Runner service (${SERVICE_ARN})..."
  aws apprunner start-deployment --service-arn "${SERVICE_ARN}" --region "${AWS_REGION}"
fi

echo "=== Deployment Triggered Successfully ==="
echo "Check progress via: aws apprunner list-services --region ${AWS_REGION}"
