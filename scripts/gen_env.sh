#!/bin/bash

generate_password() {
    local length=${1:-20}
    < /dev/urandom tr -dc 'A-Za-z0-9!@#$%^&*' | head -c "$length"
}

generate_secret() {
    < /dev/urandom tr -dc 'A-Za-z0-9' | head -c 64
}

echo "======================================"
echo "   .env generator for AutoReviewer"
echo "======================================"
echo ""

echo "--- AI ---"
read -p "AI_LLM_API_KEY: " AI_LLM_API_KEY
while [ -z "$AI_LLM_API_KEY" ]; do
    read -p "AI_LLM_API_KEY (required): " AI_LLM_API_KEY
done

echo ""
echo "--- Email ---"
read -p "EMAIL_FROM: " EMAIL_FROM
while [ -z "$EMAIL_FROM" ]; do
    read -p "EMAIL_FROM (required): " EMAIL_FROM
done

read -p "EMAIL_MAILEROO_API_KEY: " EMAIL_MAILEROO_API_KEY
while [ -z "$EMAIL_MAILEROO_API_KEY" ]; do
    read -p "EMAIL_MAILEROO_API_KEY (required): " EMAIL_MAILEROO_API_KEY
done

AUTH_SECRET_KEY=$(generate_secret)
POSTGRES_PASSWORD=$(generate_password)
S3_ACCESS_KEY=$(generate_password 20)
S3_SECRET_KEY=$(generate_password 32)
MINIO_ROOT_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)

cat > ".env" << EOF
#Auth
AUTH_SECRET_KEY=$AUTH_SECRET_KEY

# logging
LOG_LEVEL=DEBUG
LOG_FORMAT=console

LOG_LOKI_URL=http://loki:3100
LOG_LOKI_ENABLED=false
LOG_LOKI_BATCH_SIZE=50
LOG_LOKI_MAX_BUFFER_SIZE=1000
LOG_LOKI_FLUSH_INTERVAL=5.0

# postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=autoreviewer
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=autoreviewer

# application
APP=backend
ENV=dev

# AI
AI_LLM_API_ENDPOINT=https://api.zveno.ai/v1
AI_LLM_API_KEY=$AI_LLM_API_KEY
AI_LLM_DEFAULT_MODEL=qwen/qwen3-235b-a22b-2507
AI_LLM_DEFAULT_MODEL_INPUT_TOKEN_PRICE=40
AI_LLM_DEFAULT_MODEL_OUTPUT_TOKEN_PRICE=110

# S3
S3_ENDPOINT=http://s3:9000
S3_ACCESS_KEY=<input-later>
S3_SECRET_KEY=<input-later>
S3_SOLUTIONS_BUCKET=solutions
S3_SOLUTION_ARTIFACTS_BUCKET=solution-artifacts
S3_USE_SSL=False
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD

# Email
EMAIL_FROM=$EMAIL_FROM
EMAIL_FROM_DISPLAY_NAME=AI Review Team (No Reply)
EMAIL_MAILEROO_API_KEY=$EMAIL_MAILEROO_API_KEY

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=$REDIS_PASSWORD
EOF

echo ""
echo "✅ .env file created"
echo "Specify later S3_ACCESS_KEY, S3_SECRET_KEY and create buckets solutions, solution-artifacts"