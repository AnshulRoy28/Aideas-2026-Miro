# Lambda Function for Knowledge Base Auto-Sync

## Quick Start

### Option 1: AWS Console (Easiest)

1. **Create Lambda Function**
   - Go to AWS Lambda Console
   - Click "Create function"
   - Name: `sync-knowledge-base`
   - Runtime: Python 3.12
   - Create function

2. **Upload Code**
   - Copy contents of `sync_knowledge_base.py`
   - Paste into Lambda editor
   - Click "Deploy"

3. **Set Environment Variables**
   - Go to Configuration → Environment variables
   - Add:
     - `KNOWLEDGE_BASE_ID` = your_kb_id
     - `DATA_SOURCE_ID` = your_ds_id
     - `AWS_REGION` = us-east-1

4. **Add S3 Trigger**
   - Click "Add trigger"
   - Select S3
   - Bucket: `my-nova-rag-data`
   - Events: PUT, DELETE
   - Suffix: `.pdf`
   - Add

5. **Done!** Upload a file to test

### Option 2: AWS CLI

```bash
cd lambda

# 1. Create function (replace YOUR_ACCOUNT_ID and ROLE_ARN)
aws lambda create-function \
  --function-name sync-knowledge-base \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-bedrock-role \
  --handler sync_knowledge_base.lambda_handler \
  --zip-file fileb://function.zip \
  --region us-east-1

# 2. Set environment variables
aws lambda update-function-configuration \
  --function-name sync-knowledge-base \
  --environment Variables="{KNOWLEDGE_BASE_ID=your_kb_id,DATA_SOURCE_ID=your_ds_id,AWS_REGION=us-east-1}" \
  --region us-east-1

# 3. Grant S3 permission
aws lambda add-permission \
  --function-name sync-knowledge-base \
  --statement-id s3-trigger \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::my-nova-rag-data \
  --region us-east-1

# 4. Configure S3 notification (update s3-notification.json first)
aws s3api put-bucket-notification-configuration \
  --bucket my-nova-rag-data \
  --notification-configuration file://s3-notification.json
```

## Files

- `sync_knowledge_base.py` - Lambda function code
- `LAMBDA_SETUP.md` - Detailed setup guide
- `iam-policy.json` - Required IAM permissions
- `s3-notification.json` - S3 event configuration
- `deploy.sh` - Deployment script
- `requirements.txt` - Dependencies (boto3 included in Lambda)

## Testing

```bash
# Upload a file
python ../upload_with_metadata.py test.pdf 10 Mathematics

# Check Lambda logs
aws logs tail /aws/lambda/sync-knowledge-base --follow

# Test query after 1-2 minutes
python ../test.py "content from test.pdf"
```

## Monitoring

```bash
# View recent logs
aws logs tail /aws/lambda/sync-knowledge-base --since 1h

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=sync-knowledge-base \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Cost

- Lambda: ~$0.0000002 per invocation
- For 100 uploads/day: ~$0.006/month
- Essentially free! 🎉

## Troubleshooting

See `LAMBDA_SETUP.md` for detailed troubleshooting guide.
