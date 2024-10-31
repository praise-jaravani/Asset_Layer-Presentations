# Asset Layer

## Overview
Asset Layer is an automated document management system designed specifically for renewable energy asset teams. The system leverages advanced machine learning capabilities to streamline document handling, deadline management, and presentation assistance.

## Key Features
- **Document Management**: Automated handling and organization of renewable energy asset documents
- **Intelligent Deadline Tracking**: AI-powered detection and tracking of document deadlines
- **RAG-Enhanced Analysis**: Utilizes Retrieval Augmented Generation for context-aware document processing
- **Presentation Support**: Assists in creating and updating presentations with document-sourced information

## Technical Architecture
The system is built on three main components:

### 1. RAG (Retrieval Augmented Generation) System
- Text Generation Interface (TGI) using Llama 2 model
- Text Embedding Interface (TEI) for document vectorization
- PGVector database for efficient vector storage and retrieval

### 2. Document Processing
- Automated document type recognition
- Deadline extraction and inference
- Document context understanding
- Metadata management

### 3. Application Interface
- Command-line interface for document analysis
- Document deadline management system
- Vector-based similarity search
- Presentation assistance capabilities


## Component Description
- `rag_system.py`: Core RAG functionality including embedding generation and similarity search
- `deadline_manager.py`: Handles document deadline detection and management
- `main.py`: Command-line interface for the system
- `app.py`: Web interface implementation (alternative to CLI)

## Technology Stack
- **Language**: Python 3.10+
- **ML Models**: 
  - Llama 2 (7B Chat) for text generation
  - BAAI/bge-large-en-v1.5 for embeddings
- **Database**: PostgreSQL with pgvector extension
- **Containerization**: Docker
- **Interface**: CLI and Web (Flask)

## Setup Instructions

### Prerequisites
- Docker installed
- Python 3.10+
- Git
- At least 16GB RAM recommended
- HuggingFace account and token (for Llama 2 access)

### 1. Create Project Directory & Clone Repository
```bash
# Create and navigate to project directory
mkdir Asset_Layer
cd Asset_Layer
# This part is optional.

# Clone repository (if using version control)
git clone https://github.com/praise-jaravani/Asset_Layer
```

### 2. Set Up Python Virtual Environment
```bash
# Install required system packages
sudo apt-get update
sudo apt-get install python3-tk tk-dev

# Create virtual environment
python3 -m venv env

# Activate virtual environment
source env/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Set Up Docker Containers

Before this, make sure you've installed Docker and/or Docker Desktop on your local machine first.

#### 3.1 Text Generation Interface (TGI)

If you have a beefy computer that has a dedicted GPU, you can attempt to use the Llama model.
```bash
# Set HuggingFace token
export HF_TOKEN=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

# Pull and run TGI container
docker run -d -p 9001:80 \
    --name local-tgi \
    -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id meta-llama/Llama-2-7b-chat-hf \
    --max-input-tokens 1024 --max-total-tokens 2048
```

However, if not, you should instead use the TinyLlama model that runs on CPU.
```bash
# Pull and run TGI container
docker run -d -p 9001:80 \
    --name local-tgi \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    --max-input-tokens 1024 \
    --max-total-tokens 2048
```

#### 3.2 Text Embedding Interface (TEI)
```bash
# Create data directory
mkdir -p RAG/data

# Pull and run TEI container
docker run -d -p 9002:80 \
    --name cpu-tei \
    -v $PWD/RAG/data:/data \
    --pull always ghcr.io/huggingface/text-embeddings-inference:cpu-1.2 \
    --model-id BAAI/bge-large-en-v1.5
```

#### 3.3 Vector Database
```bash
# Pull and run PGVector container
docker run \
    --name postgres_vectordb \
    -d \
    -e POSTGRES_PASSWORD=postgres \
    -p 9003:5432 \
    pgvector/pgvector:pg16
```

### 4. Verify Container Status
```bash
# Check if all containers are running
docker ps

# Check container logs if needed
docker logs local-tgi -f
docker logs cpu-tei -f
docker logs postgres_vectordb -f
```

### 5. Load Test Documents (Optional)
```bash
# Create test documents directory
mkdir -p RAG/data/test-documents

# Run document loader
python load_documents.py --directory RAG/data/test-documents
```

### 6. Running the Application
#### Command Line Interface
```bash
# Run the CLI version
python main.py
```

#### Web Interface (Alternative)
For this, cd into the app.
```bash
# Run the Flask web application
python app.py
```

### 7. Stopping the Application
```bash
# Stop all containers
docker stop local-tgi cpu-tei postgres_vectordb

# Remove containers (if needed)
docker rm local-tgi cpu-tei postgres_vectordb

# Deactivate virtual environment
deactivate
```

## Troubleshooting

### Common Issues and Solutions:

1. **Container Startup Failures**
  * Check container logs using `docker logs <container-name>`
  * Ensure ports 9001, 9002, and 9003 are available

2. **Memory Issues**
  * Ensure sufficient RAM is available
  * Monitor resource usage with `docker stats`

3. **Permission Issues**
  * Ensure proper file permissions in RAG/data directory
  * Check Docker permissions

4. **Database Connection Issues**
  * Verify PostgreSQL container is running
  * Check connection string in configuration