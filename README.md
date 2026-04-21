# Supplier Delay Monitor

Production-ready MVP for tracking supplier shipping delays, planner ownership, actions, comments, and attachments.

## Architecture

- Frontend: React, TypeScript, Vite
- Backend: Python AWS Lambda behind API Gateway
- Infrastructure: AWS CDK, no manual AWS resource creation
- Delay source: Snowflake, read-only
- Mutable data: DynamoDB
- Attachments: S3 presigned uploads
- Secrets: AWS Secrets Manager
- Auth: Amazon Cognito with `Viewer`, `Planner`, and `Admin` groups

## Repository

```text
backend/     Lambda application code
frontend/    React application
infra/       AWS CDK app
```

## Prerequisites

- AWS credentials configured locally
- Node.js 20+
- Python 3.11+
- AWS CDK bootstrapped once per account/region:

```bash
npm install -g aws-cdk
cdk bootstrap
```

## Deploy

```bash
cd frontend
npm install
npm run build

cd infra
npm install
npm run build
npx cdk deploy \
  -c snowflakeSecretName=supplier-delay/snowflake \
  -c allowedOrigins=https://your-internal-domain.example
```

The CDK stack provisions Cognito, API Gateway, Lambda, DynamoDB tables, S3, CloudFront frontend hosting, IAM, and references the Snowflake secret by name. The deployed frontend calls `/api/*` through CloudFront, which routes to API Gateway.

## Snowflake Secret

Create the secret value through your normal secret management process before deploying application traffic. The secret itself is referenced by CDK and read only at Lambda runtime.

Expected JSON:

```json
{
  "account": "abc123.eu-west-1",
  "user": "SUPPLIER_DELAY_APP",
  "password": "replace-me",
  "warehouse": "COMPUTE_WH",
  "database": "SUPPLY_CHAIN",
  "schema": "PUBLIC",
  "role": "APP_READONLY",
  "query": "select supplier_code, supplier_name, plant_code, planner_code, part_number, shipment_no, planned_ship_date, actual_ship_date, delay_days from SUPPLIER_DELAYS"
}
```

Do not commit Snowflake credentials.

## Local Development

Backend mock mode:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
MOCK_SNOWFLAKE=true ACTIONS_TABLE=local-actions COMMENTS_TABLE=local-comments ATTACHMENTS_BUCKET=local python local_server.py
```

Frontend:

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8787 npm run dev
```

For local testing against the deployed API, store a Cognito ID token in browser local storage under `supplierDelayToken`.

## API

- `GET /api/delays?planner_codes=PL01,PL02`
- `GET /api/delays/{shipment_key}`
- `GET /api/comments?shipment_key=...`
- `POST /api/comments`
- `PUT /api/comments/{id}`
- `DELETE /api/comments/{id}`
- `GET /api/planner-codes`
- `POST /api/attachments/presign`

## Comment Ordering Contract

Comments are ordered by immutable `created_at` descending, then `id` descending. Edits update content in place and never alter ordering.

# supplier-delay-app-aws
