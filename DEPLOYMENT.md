# Deployment Guide for RAG Chatbot

This guide covers deploying the RAG chatbot on AWS, GCP, and Azure.

## Table of Contents

1. [Local Development with Docker](#local-development-with-docker)
2. [AWS Deployment](#aws-deployment)
3. [GCP Deployment](#gcp-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Monitoring & Logging](#monitoring--logging)

---

## Local Development with Docker

### Prerequisites
- Docker & Docker Compose installed
- Ollama running locally (port 11434)

### Building and Running

```bash
# Build the Docker image
docker build -t rag-chatbot:latest .

# Run with docker-compose
docker-compose up --build

# Or run manually
docker run -it \
  -v ./chroma_db_bpe:/app/chroma_db_bpe \
  -e OLLAMA_HOST=host.docker.internal:11434 \
  rag-chatbot:latest
```

### Troubleshooting

**Container can't reach Ollama:**
```bash
# On Windows/Mac, use host.docker.internal
# On Linux, use the host's IP or create a shared network
docker network create rag-net
docker run --network rag-net -e OLLAMA_HOST=ollama:11434 rag-chatbot
```

---

## AWS Deployment

### Architecture

```
S3 → Lambda (Process) → RDS (pgvector) → Lambda (Query) → SageMaker LLM
```

### Step 1: Prepare Resources

```bash
# 1. Create S3 bucket for documents
aws s3api create-bucket \
  --bucket rag-chatbot-docs \
  --region us-east-1

# 2. Create RDS cluster with pgvector
aws rds create-db-cluster \
  --db-cluster-identifier rag-vector-db \
  --engine aurora-postgresql \
  --engine-version 14.6 \
  --master-username postgres \
  --master-user-password YourSecurePassword123
```

### Step 2: Deploy LLM

**Option A: Use Bedrock (Managed Service)**
```python
from langchain_community.llms.bedrock import Bedrock

llm = Bedrock(
    model_id="anthropic.claude-3-sonnet",
    region_name="us-east-1"
)
```

**Option B: Deploy to SageMaker**
```python
from langchain_community.llms.sagemaker_endpoint import SagemakerEndpoint

llm = SagemakerEndpoint(
    endpoint_name="llama2-endpoint",
    region_name="us-east-1",
    model_kwargs={"temperature": 0.7}
)
```

### Step 3: Create Lambda Functions

**Document Processing Lambda:**
```python
# lambda_process_documents.py
import json
import boto3
from src.data_loader import load_pdf
from src.text_splitter import split_documents
from src.vectorstore import create_vectorstore

s3 = boto3.client('s3')
rds = boto3.client('rds')

def lambda_handler(event, context):
    """Process uploaded documents and store embeddings."""
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    pdf_content = obj['Body'].read()
    
    # Process
    docs = load_pdf(pdf_content)
    splits = split_documents(docs)
    
    # Store in RDS
    vectorstore = create_vectorstore(splits, connection=rds_connection)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'chunks': len(splits)})
    }
```

**Query Lambda:**
```python
# lambda_query.py
from src.rag_chain import build_rag_chain

def lambda_handler(event, context):
    """Handle user queries."""
    question = json.loads(event['body'])['question']
    
    vectorstore = load_vectorstore_from_rds()
    rag_chain = build_rag_chain(vectorstore)
    
    answer = rag_chain.invoke(question)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'answer': answer}),
        'headers': {'Content-Type': 'application/json'}
    }
```

### Step 4: Deploy with API Gateway

```bash
# Create REST API
aws apigateway create-rest-api --name rag-api

# Create resource
aws apigateway create-resource --rest-api-id xxx --parent-id yyy --path-part query

# Create POST method + Lambda integration
# (Use AWS Console for easier setup)
```

### Step 5: Cost Optimization

```bash
# Use Lambda reserved concurrency to control costs
aws lambda put-function-concurrency \
  --function-name query-lambda \
  --reserved-concurrent-executions 10

# Use Aurora Serverless v2 for auto-scaling DB
aws rds create-db-cluster \
  --db-cluster-class db.serverless \
  --scaling-configuration MinACU=0.5,MaxACU=2
```

---

## GCP Deployment

### Architecture

```
Cloud Storage → Cloud Functions → Vertex AI Search → Cloud Run → Vertex AI LLM
```

### Step 1: Enable APIs

```bash
gcloud services enable \
  storage-api \
  cloudfunctions \
  run.googleapis.com \
  aiplatform.googleapis.com
```

### Step 2: Create Cloud Function for Processing

```python
# main.py (Cloud Function)
from google.cloud import storage
from src.data_loader import load_pdf
from src.text_splitter import split_documents
from src.vectorstore import create_vectorstore

def process_pdf(request):
    """HTTP Cloud Function triggered by Cloud Scheduler."""
    storage_client = storage.Client()
    bucket = storage_client.bucket('rag-docs')
    
    for blob in bucket.list_blobs():
        pdf_content = blob.download_as_bytes()
        docs = load_pdf(pdf_content)
        splits = split_documents(docs)
        
        # Store in Vertex AI Vector Search
        create_vectorstore(splits, vector_db_id='rag-db')
    
    return 'OK'
```

### Step 3: Deploy API on Cloud Run

```bash
# Create requirements.txt with Vertex AI dependencies
cat >> requirements.txt << EOF
google-cloud-aiplatform
google-cloud-storage
EOF

# Deploy
gcloud run deploy rag-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 4: Use Vertex AI LLM

```python
from google.cloud import aiplatform

aiplatform.init(project='your-project', location='us-central1')

llm = aiplatform.Vertex(
    model_name='gemini-pro',
    temperature=0.7
)
```

---

## Azure Deployment

### Architecture

```
Blob Storage → Azure Functions → Cognitive Search → App Service → Azure OpenAI
```

### Step 1: Create Resources

```bash
# Create resource group
az group create --name rag-rg --location eastus

# Create storage account
az storage account create --name ragstorage --resource-group rag-rg

# Create Cognitive Search
az search service create \
  --name rag-search \
  --resource-group rag-rg \
  --sku standard
```

### Step 2: Deploy Functions

```bash
# Create Function App
az functionapp create \
  --resource-group rag-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --name rag-functions
```

### Step 3: Configure Azure OpenAI

```python
from langchain_openai import AzureOpenAI

llm = AzureOpenAI(
    deployment_name="gpt-4",
    api_version="2024-02-15",
    azure_endpoint="https://your-resource.openai.azure.com"
)
```

---

## Monitoring & Logging

### AWS CloudWatch

```python
import watchtower
import logging

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        watchtower.CloudWatchLogHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Query executed", extra={
    'query': question,
    'latency_ms': latency,
    'tokens_used': token_count
})
```

### GCP Cloud Logging

```python
from google.cloud import logging as cloud_logging

logging_client = cloud_logging.Client()
logging_client.setup_logging()

import logging
logger = logging.getLogger(__name__)
logger.info("Query executed", extra={'query': question})
```

### Azure Monitor

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger.addHandler(AzureLogHandler(
    connection_string='your-app-insights-connection-string'
))
```

### Metrics to Track

- Query latency (p50, p95, p99)
- Retrieval quality (NDCG, MRR)
- LLM token usage
- Error rate
- Vector DB query time
- Embedding time

---

## Cost Comparison

| Provider | Component | Monthly Cost (1K queries/day) |
|----------|-----------|------|
| **AWS** | Lambda | $20 |
| | RDS Aurora | $200 |
| | SageMaker | $300 |
| | **Total** | **$520** |
| **GCP** | Cloud Functions | $15 |
| | Vertex AI Search | $200 |
| | Vertex AI LLM | $300 |
| | **Total** | **$515** |
| **Azure** | Functions | $20 |
| | Cognitive Search | $200 |
| | Azure OpenAI | $300 |
| | **Total** | **$520** |

---

## Next Steps

1. **Start with local Docker** to validate the system
2. **Choose a cloud provider** based on your needs
3. **Deploy the processing pipeline** first
4. **Add monitoring and logging**
5. **Optimize costs** with appropriate scaling policies
