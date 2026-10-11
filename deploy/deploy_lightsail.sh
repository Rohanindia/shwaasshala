#!/usr/bin/env bash
# Deploy ShwaasShala to AWS Lightsail Containers
set -euo pipefail

SERVICE_NAME="shwaasshala-service"
CONTAINER_NAME="shwaasshala-app"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "=== 1. Creating Lightsail Container Service (Micro 0.25 vCPU, 512MB) ==="
aws lightsail get-container-services --service-name "${SERVICE_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1 || \
aws lightsail create-container-service \
  --service-name "${SERVICE_NAME}" \
  --power micro \
  --scale 1 \
  --region "${AWS_REGION}"

echo "=== 2. Building Docker image locally ==="
docker build -t shwaasshala:latest .

echo "=== 3. Pushing Image directly to Lightsail Container Registry ==="
aws lightsail push-container-image \
  --service-name "${SERVICE_NAME}" \
  --label latest \
  --image shwaasshala:latest \
  --region "${AWS_REGION}"

echo "=== 4. Fetching Image Tag and Deploying Container ==="
IMAGE_NAME=$(aws lightsail get-container-images --service-name "${SERVICE_NAME}" --region "${AWS_REGION}" --query "containerImages[0].image" --output text)

cat <<EOF > /tmp/lightsail-containers.json
{
  "containers": {
    "${CONTAINER_NAME}": {
      "image": "${IMAGE_NAME}",
      "environment": {
        "MODEL_PROVIDER": "bedrock",
        "AWS_REGION": "${AWS_REGION}",
        "ENVIRONMENT": "production"
      },
      "ports": {
        "8000": "HTTP"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "${CONTAINER_NAME}",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/api/health",
      "intervalSeconds": 30,
      "timeoutSeconds": 5,
      "healthyThreshold": 2,
      "unhealthyThreshold": 3
    }
  }
}
EOF

aws lightsail create-container-service-deployment \
  --service-name "${SERVICE_NAME}" \
  --cli-input-json file:///tmp/lightsail-containers.json \
  --region "${AWS_REGION}"

echo "=== Lightsail Deployment Initiated ==="
aws lightsail get-container-services --service-name "${SERVICE_NAME}" --region "${AWS_REGION}" --query "containerServices[0].url" --output text
