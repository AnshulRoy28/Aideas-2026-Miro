# Lambda Function Setup for Knowledge Base Auto-Sync

## Why Lambda is Better

✅ **Event-driven** - Triggers automatically on S3 changes  
✅ **Serverless** - No server to manage  
✅ **Scalable** - Handles any upload volume  
✅ **Cost-effective** - Only pay when triggered  
✅ **Reliable** - AWS manages retries and monitoring  
✅ **Decoupled** - Works independently of your application  

## Architecture

```
S3 Bucket (my-nova-rag-data)
    ↓ (PUT/DELETE event)
Lambda Function (sync_knowledge_base)
    ↓ (start_ingestion_job)
Bedrock Knowledge Base
    ↓ (syncs data)
Updated Knowledge Base ✅
```

## Setup Instructions

### Step 1: Create Lambda Function

#### Option A: AWS Console

1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `sync-knowledge-base`
5. Runtime: `Python 3.12`
6. Architecture: `x86_64`
7. Click "Create function"

#### Option B: AWS CLI

```bash
# Create function
aws lambda create-function \
  --function-name sync-knowledge-base \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-bedrock-role \
  --handler sync_knowledge_base.lambda_handler \
  --zip-file fileb://function.zip \
  --region us-east-1
```

### Step 2: Upload Function Code

#### Option A: AWS Console

1. In Lambda function page, go to "Code" tab
2. Copy contents of `lambda/sync_knowledge_base.py`
3. Paste into `lambda_function.py` in the editor
4. Click "Deploy"

#### Option B: AWS CLI

```bash
# Package function
cd lambda
zip function.zip sync_knowledge_base.py

# Upload
aws lambda update-function-code \
  --function-name sync-knowledge-base \
  --zip-file fileb://function.zip \
  --region us-east-1
```

### Step 3: Configure Environment Variables

In Lambda Console → Configuration → Environment variables:

```
KNOWLEDGE_BASE_ID = your_knowledge_base_id
DATA_SOURCE_ID = your_data_source_id
AWS_REGION = us-east-1
```

Or via CLI:

```bash
aws lambda update-function-configuration \
  --function-name sync-knowledge-base \
  --environment Variables="{KNOWLEDGE_BASE_ID=your_kb_id,DATA_SOURCE_ID=your_ds_id,AWS_REGION=us-east-1}" \
  --region us-east-1
```

### Step 4: Set Up IAM Role

Lambda needs permissions to:
- Read S3 events
- Start Bedrock ingestion jobs
- Write CloudWatch logs

#### Create IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:StartIngestionJob",
        "bedrock:GetIngestionJob"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:knowledge-base/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-nova-rag-data/*"
    }
  ]
}
```

#### Attach to Lambda Role

1. Go to IAM Console
2. Find your Lambda execution role
3. Attach the policy above

### Step 5: Configure S3 Event Trigger

#### Option A: AWS Console

1. In Lambda function, click "Add trigger"
2. Select "S3"
3. Bucket: `my-nova-rag-data`
4. Event types: 
   - ✅ `PUT` (for uploads)
   - ✅ `DELETE` (for deletions)
5. Prefix: (leave empty to trigger on all files)
6. Suffix: `.pdf` (optional - only trigger on PDFs)
7. Click "Add"

#### Option B: AWS CLI

```bash
# Add S3 notification configuration
aws s3api put-bucket-notification-configuration \
  --bucket my-nova-rag-data \
  --notification-configuration file://s3-notification.json
```

**s3-notification.json:**
```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:sync-knowledge-base",
      "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".pdf"
            }
          ]
        }
      }
    }
  ]
}
```

### Step 6: Grant S3 Permission to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name sync-knowledge-base \
  --statement-id s3-trigger \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::my-nova-rag-data \
  --region us-east-1
```

## Testing

### Test 1: Upload a File

```bash
python upload_with_metadata.py test.pdf 10 Mathematics
```

### Test 2: Check Lambda Logs

```bash
aws logs tail /aws/lambda/sync-knowledge-base --follow
```

You should see:
```
✅ Ingestion job started successfully
Job ID: ABC123
Status: STARTING
```

### Test 3: Verify Knowledge Base

Wait 1-2 minutes, then:

```bash
python test.py "content from test.pdf"
```

## Monitoring

### CloudWatch Logs

View Lambda execution logs:
```bash
aws logs tail /aws/lambda/sync-knowledge-base --follow
```

### Lambda Metrics

- Invocations
- Duration
- Errors
- Throttles

### Cost Estimate

- **Lambda**: ~$0.0000002 per invocation
- **S3 Events**: Free
- **Bedrock Ingestion**: Varies by data size

For 100 uploads/day: **~$0.006/month** (essentially free!)

## Advantages Over Server-Based Sync

| Feature | Lambda | Server-Based |
|---------|--------|--------------|
| Setup | One-time | Code in every upload |
| Reliability | AWS managed | Your responsibility |
| Scaling | Automatic | Manual |
| Cost | Pay per use | Always running |
| Maintenance | None | Update code |
| Monitoring | CloudWatch | Custom |
| Retries | Automatic | Manual |

## Troubleshooting

### Lambda not triggering

**Check:**
1. S3 event notification is configured
2. Lambda has permission to be invoked by S3
3. Event types include PUT and DELETE
4. Filter matches your files (.pdf)

### Permission errors

**Check:**
1. Lambda execution role has bedrock permissions
2. Environment variables are set
3. Knowledge Base ID and Data Source ID are correct

### Sync not working

**Check:**
1. Lambda logs in CloudWatch
2. Ingestion job status in Bedrock console
3. Data source is connected to correct S3 bucket

## Cleanup Server Code (Optional)

Since Lambda handles sync now, you can remove sync code from `server.py`:

1. Remove `trigger_knowledge_base_sync()` function
2. Remove sync calls from upload/delete endpoints
3. Remove `bedrock_agent_client` initialization
4. Remove `DATA_SOURCE_ID` from `.env`

Keep `KNOWLEDGE_BASE_ID` for RAG queries in `test.py`.

## Summary

✅ Lambda function created  
✅ S3 trigger configured  
✅ Automatic sync on upload/delete  
✅ Serverless and scalable  
✅ Cost-effective  
✅ No code changes needed  

Your Knowledge Base now syncs automatically via Lambda! 🎉
