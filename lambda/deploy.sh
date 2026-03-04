#!/bin/bash

# Lambda Deployment Script for Knowledge Base Auto-Sync
# This script packages and deploys the Lambda function

set -e

echo "================================================"
echo "  Lambda Deployment - Knowledge Base Sync"
echo "================================================"
echo ""

# Configuration
FUNCTION_NAME="sync-knowledge-base"
RUNTIME="python3.12"
HANDLER="sync_knowledge_base.lambda_handler"
REGION="us-east-1"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Check if required files exist
if [ ! -f "sync_knowledge_base.py" ]; then
    echo "❌ sync_knowledge_base.py not found"
    exit 1
fi

echo "📦 Packaging Lambda function..."
zip -q function.zip sync_knowledge_base.py
echo "✅ Package created: function.zip"
echo ""

# Check if function exists
echo "🔍 Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "📝 Function exists. Updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION
    echo "✅ Function code updated"
else
    echo "❌ Function does not exist. Please create it first using AWS Console or:"
    echo ""
    echo "aws lambda create-function \\"
    echo "  --function-name $FUNCTION_NAME \\"
    echo "  --runtime $RUNTIME \\"
    echo "  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-bedrock-role \\"
    echo "  --handler $HANDLER \\"
    echo "  --zip-file fileb://function.zip \\"
    echo "  --region $REGION"
    echo ""
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set environment variables in Lambda Console:"
echo "   - KNOWLEDGE_BASE_ID"
echo "   - DATA_SOURCE_ID"
echo "   - AWS_REGION"
echo ""
echo "2. Configure S3 trigger (if not already done)"
echo ""
echo "3. Test by uploading a file to S3"
echo ""
echo "View logs:"
echo "aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo ""

# Cleanup
rm function.zip
