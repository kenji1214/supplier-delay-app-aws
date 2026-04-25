# Supplier Backorder Monitor

Single-container React + FastAPI app prepared for both localhost Docker execution and AWS container deployment.

## Runtime behavior

- `ENV=local` enables local-oriented behavior such as local CORS defaults and development-only debug access.
- `ENV=aws` is the deployment mode for AWS containers.
- The backend listens on `0.0.0.0` and reads the HTTP port from `PORT`.
- Snowflake credentials are read from environment variables only.
- AWS deployment settings are also read from environment variables.
- Health endpoint: `GET /health`

## Environment files

- Local Docker defaults: [.env.local](/Users/Project/supplier-delay-app-ver1/.env.local)
- AWS example template: [.env.aws.example](/Users/Project/supplier-delay-app-ver1/.env.aws.example)

Do not put real secrets in the repo. For AWS, create your own runtime environment from `.env.aws.example` and supply the real values through App Runner or another secret source.

## Local run

Run the backend directly:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ENV=local PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker build

Build the production image from the repo root:

```bash
docker build -t supplier-delay-app .
```

## Docker run

Run locally with the provided local environment file:

```bash
docker run --rm \
  --env-file .env.local \
  -p 8000:8000 \
  supplier-delay-app
```

Open `http://localhost:8000` and check `http://localhost:8000/health`.

## ECR push

Set the AWS values first:

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=123456789012
export AWS_ECR_REPOSITORY=supplier-delay-app
```

Create the repository if needed:

```bash
aws ecr create-repository --repository-name "$AWS_ECR_REPOSITORY" --region "$AWS_REGION"
```

Authenticate Docker to ECR:

```bash
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

Tag and push:

```bash
docker tag supplier-delay-app:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_ECR_REPOSITORY:latest"
```

## App Runner deployment

Set the AWS deployment variables:

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=123456789012
export AWS_ECR_REPOSITORY=supplier-delay-app
export AWS_APPRUNNER_SERVICE_NAME=supplier-delay-app
```

Create the service from the pushed image:

```bash
aws apprunner create-service \
  --region "$AWS_REGION" \
  --service-name "$AWS_APPRUNNER_SERVICE_NAME" \
  --source-configuration '{
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::'"$AWS_ACCOUNT_ID"':role/AppRunnerECRAccessRole"
    },
    "AutoDeploymentsEnabled": true,
    "ImageRepository": {
      "ImageIdentifier": "'"$AWS_ACCOUNT_ID"'.dkr.ecr.'"$AWS_REGION"'.amazonaws.com/'"$AWS_ECR_REPOSITORY"':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "ENV": "aws",
          "PORT": "8000",
          "USE_MOCK_DATA": "false",
          "SQLITE_PATH": "/app/data/comments.db",
          "SNOWFLAKE_ACCOUNT": "",
          "SNOWFLAKE_USER": "",
          "SNOWFLAKE_PASSWORD": "",
          "SNOWFLAKE_WAREHOUSE": "",
          "SNOWFLAKE_DATABASE": "",
          "SNOWFLAKE_SCHEMA": "",
          "SNOWFLAKE_ROLE": "",
          "AWS_REGION": "'"$AWS_REGION"'",
          "AWS_ACCOUNT_ID": "'"$AWS_ACCOUNT_ID"'",
          "AWS_ECR_REPOSITORY": "'"$AWS_ECR_REPOSITORY"'",
          "AWS_APPRUNNER_SERVICE_NAME": "'"$AWS_APPRUNNER_SERVICE_NAME"'"
        }
      }
    }
  }'
```

In production, move secrets such as `SNOWFLAKE_PASSWORD` into AWS Secrets Manager or App Runner secret references instead of plain environment variables.

## Required environment variables

Application:

- `ENV=local|aws`
- `PORT`
- `SQLITE_PATH`
- `USE_MOCK_DATA`
- `CURRENT_USER`
- `CORS_ORIGINS`

Snowflake:

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `SNOWFLAKE_ROLE`

AWS deployment metadata:

- `AWS_REGION`
- `AWS_ACCOUNT_ID`
- `AWS_ECR_REPOSITORY`
- `AWS_APPRUNNER_SERVICE_NAME`
