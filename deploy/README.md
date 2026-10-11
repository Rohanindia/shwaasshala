# ShwaasShala AWS Deployment Guide

This directory contains production deployment scripts for running ShwaasShala on AWS.

> **Note on Hackathon Eligibility**:
> ShwaasShala natively qualifies for the WeMakeDevs x AWS Hackathon by utilizing the **AWS open-source Strands Agents SDK (`strands-agents`)**. Deploying onto AWS cloud infrastructure is completely optional.

---

## Deployment Option A: AWS App Runner (Recommended for Serverless Containers)

AWS App Runner provides fully managed container execution with automatic scaling, TLS certificates, and zero infrastructure maintenance.

### Prerequisites
1. AWS CLI installed and configured (`aws configure`)
2. Docker running locally
3. AWS IAM permissions for App Runner and ECR

### One-Command Deployment
```bash
chmod +x deploy/deploy_apprunner.sh
./deploy/deploy_apprunner.sh
```

---

## Deployment Option B: AWS Lightsail Containers (Low-Cost / Student Friendly)

AWS Lightsail Containers costs as little as $7/month for a micro container instance.

### Prerequisites
1. AWS CLI with `lightsailctl` plugin installed:
   ```bash
   # On macOS
   brew install aws-lightsailctl
   # Or download from AWS documentation
   ```

### Execution
```bash
chmod +x deploy/deploy_lightsail.sh
./deploy/deploy_lightsail.sh
```

---

## IAM Role for Amazon Bedrock (Optional)
If you enable live Bedrock model calls in AWS:
Attach the managed policy `AmazonBedrockFullAccess` (or scoped `bedrock:InvokeModel`) to your App Runner instance execution role.
