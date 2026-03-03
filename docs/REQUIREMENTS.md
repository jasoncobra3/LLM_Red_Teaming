# Requirements Documentation

This document outlines system requirements, dependencies, and environment setup for different deployment scenarios.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Dependencies](#python-dependencies)
3. [Environment-Specific Requirements](#environment-specific-requirements)
4. [API Requirements](#api-requirements)
5. [Optional Dependencies](#optional-dependencies)
6. [Hardware Requirements](#hardware-requirements)

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, macOS 10.15+, Ubuntu 20.04+ |
| **Python** | 3.10.0 or higher |
| **RAM** | 4 GB |
| **Disk Space** | 2 GB free |
| **Network** | Internet connection required |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **OS** | Windows 11, macOS 13+, Ubuntu 22.04+ |
| **Python** | 3.11.x |
| **RAM** | 8 GB or more |
| **Disk Space** | 5 GB free |
| **Network** | High-speed internet |
| **CPU** | 4+ cores |

## Python Dependencies

### Core Dependencies

```txt
# requirements.txt

# Web Frameworks
streamlit>=1.32.0
fastapi>=0.110.0
uvicorn[standard]>=0.28.0

# LLM Frameworks
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-anthropic>=0.1.0
langchain-google-genai>=0.0.11
langchain-groq>=0.0.1
deepeval>=1.2.0

# AI/ML Libraries
openai>=1.12.0
anthropic>=0.18.0
google-generativeai>=0.4.0

# Database
sqlalchemy>=2.0.27
alembic>=1.13.0

# Authentication
passlib>=1.7.4
bcrypt>=4.1.0
python-jose[cryptography]>=3.3.0

# PDF Generation
reportlab>=4.1.0
pypdf>=4.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
requests>=2.31.0
httpx>=0.26.0
aiohttp>=3.9.0

# Async Support
asyncio>=3.4.3
anyio>=4.2.0

# Data Processing
pandas>=2.2.0
numpy>=1.26.0

# Visualization
plotly>=5.19.0
altair>=5.2.0

# Logging & Monitoring
loguru>=0.7.0
python-json-logger>=2.0.7

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```

### Version Compatibility Matrix

| Python | Streamlit | LangChain | OpenAI | FastAPI |
|--------|-----------|-----------|--------|---------|
| 3.10   | ✅ 1.32+  | ✅ 0.1.0+ | ✅ 1.12+ | ✅ 0.110+ |
| 3.11   | ✅ 1.32+  | ✅ 0.1.0+ | ✅ 1.12+ | ✅ 0.110+ |
| 3.12   | ✅ 1.32+  | ✅ 0.1.0+ | ✅ 1.12+ | ✅ 0.110+ |

## Environment-Specific Requirements

### Development Environment

```bash
# requirements-dev.txt

# Include all core requirements
-r requirements.txt

# Development Tools
black>=24.1.0               # Code formatting
isort>=5.13.0               # Import sorting
flake8>=7.0.0               # Linting
mypy>=1.8.0                 # Type checking
pylint>=3.0.0               # Code analysis

# Testing
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0
pytest-timeout>=2.2.0
coverage>=7.4.0

# Debugging
ipdb>=0.13.0
pdb++>=0.10.0

# Documentation
sphinx>=7.2.0
sphinx-rtd-theme>=2.0.0
mkdocs>=1.5.0
mkdocs-material>=9.5.0

# Pre-commit hooks
pre-commit>=3.6.0

# Performance profiling
py-spy>=0.3.0
memory-profiler>=0.61.0
```

### Production Environment

```bash
# requirements-prod.txt

# Include core requirements
-r requirements.txt

# Production Server
gunicorn>=21.2.0            # WSGI server
uvicorn[standard]>=0.28.0   # ASGI server

# Monitoring
prometheus-client>=0.19.0
sentry-sdk>=1.40.0
newrelic>=9.6.0

# Security
python-dotenv>=1.0.0
cryptography>=42.0.0
PyJWT>=2.8.0

# Database
psycopg2-binary>=2.9.9      # PostgreSQL
redis>=5.0.0                # Caching

# Performance
gevent>=23.9.0
greenlet>=3.0.0
```

### Staging Environment

```bash
# requirements-staging.txt

# Same as production plus testing tools
-r requirements-prod.txt

# Performance testing
locust>=2.20.0
pytest-benchmark>=4.0.0

# Load testing
k6>=0.46.0
```

## API Requirements

### Required API Keys

#### OpenAI
```env
OPENAI_API_KEY=sk-proj-...
# Get from: https://platform.openai.com/api-keys
# Models: GPT-4, GPT-3.5-turbo, GPT-4o
# Pricing: https://openai.com/pricing
```

#### Groq
```env
GROQ_API_KEY=gsk_...
# Get from: https://console.groq.com/keys
# Models: Llama 3.x, Mixtral, Gemma
# Free tier: 100,000 tokens/day
```

#### Azure OpenAI (Optional)
```env
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_VERSION=2023-05-15
# Get from: https://portal.azure.com
# Requires Azure subscription
```

#### Anthropic Claude (Optional)
```env
ANTHROPIC_API_KEY=sk-ant-...
# Get from: https://console.anthropic.com/
# Models: Claude 3 Opus, Sonnet, Haiku
```

#### Google Gemini (Optional)
```env
GOOGLE_API_KEY=...
# Get from: https://makersuite.google.com/app/apikey
# Models: Gemini Pro, Gemini Pro Vision
```

### API Rate Limits

| Provider | Free Tier | Paid Tier |
|----------|-----------|-----------|
| OpenAI | 3 RPM | 10,000+ RPM |
| Groq | 30 RPM, 100K TPD | Custom |
| Azure OpenAI | N/A | Custom |
| Anthropic | 5 RPM | Custom |
| Google Gemini | 60 RPM | Custom |

*RPM = Requests Per Minute, TPD = Tokens Per Day*

## Optional Dependencies

### Local Model Support

```bash
# Ollama (Local LLMs)
pip install ollama

# Setup:
# 1. Install Ollama: https://ollama.ai/download
# 2. Pull models: ollama pull llama3
# 3. Configure: OLLAMA_BASE_URL=http://localhost:11434
```

### Enhanced PDF Reports

```bash
# Advanced PDF features
pip install weasyprint>=60.0
pip install pillow>=10.0.0
pip install matplotlib>=3.8.0
```

### Database Alternatives

```bash
# PostgreSQL
pip install psycopg2-binary>=2.9.9
pip install asyncpg>=0.29.0

# MySQL
pip install pymysql>=1.1.0
pip install mysql-connector-python>=8.3.0

# MongoDB
pip install pymongo>=4.6.0
pip install motor>=3.3.0  # Async
```

### Caching Systems

```bash
# Redis
pip install redis>=5.0.0
pip install aioredis>=2.0.0

# Memcached
pip install pymemcache>=4.0.0
```

### Message Queues

```bash
# Celery (Task Queue)
pip install celery>=5.3.0
pip install redis>=5.0.0  # Broker

# RabbitMQ
pip install pika>=1.3.0
```

## Hardware Requirements

### Development

```
CPU: 2 cores minimum
RAM: 4 GB minimum, 8 GB recommended
Disk: 5 GB free space
    - 2 GB: Dependencies
    - 1 GB: Models cache
    - 2 GB: Logs and database
Network: Broadband internet
```

### Production (Single Server)

```
CPU: 4-8 cores
RAM: 16-32 GB
    - 8 GB: Application
    - 4 GB: Database
    - 4 GB: Cache/Buffers
Disk: 50-100 GB SSD
    - 10 GB: Application
    - 20 GB: Database
    - 20 GB: Logs
Network: 1 Gbps+
```

### Production (Distributed)

```
Load Balancer:
- CPU: 2 cores
- RAM: 4 GB
- Network: 10 Gbps

Application Servers (×3):
- CPU: 8 cores each
- RAM: 32 GB each
- Disk: 50 GB SSD each

Database Server:
- CPU: 16 cores
- RAM: 64 GB
- Disk: 500 GB SSD (RAID 10)

Cache Server (Redis):
- CPU: 4 cores
- RAM: 16 GB
- Disk: 50 GB SSD
```

## Platform-Specific Notes

### Windows

```powershell
# Python installation
# Download from: https://python.org

# Verify installation
python --version

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Windows-specific: Visual C++ may be required
# Download: https://visualstudio.microsoft.com/downloads/
# Install "Desktop development with C++"
```

**Known Issues**:
- AsyncIO event loop: Use `WindowsSelectorEventLoopPolicy`
- Some packages require Visual C++ Build Tools
- Path length limitations (enable long paths in registry)

### macOS

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# macOS-specific: Xcode Command Line Tools
xcode-select --install
```

**Known Issues**:
- M1/M2 Macs: Some packages need Rosetta 2
- SSL certificates: `pip install --upgrade certifi`

### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip

# System dependencies
sudo apt install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8501 8000

# Run application
CMD ["streamlit", "run", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./database:/app/database
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: redteaming
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Verification

### Check Installation

```python
# check_requirements.py
import sys
import importlib

REQUIRED_PACKAGES = [
    'streamlit',
    'fastapi',
    'langchain',
    'openai',
    'sqlalchemy',
]

def check_packages():
    print(f"Python Version: {sys.version}")
    print("\nChecking packages:")
    
    for package in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {package}: {version}")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")

if __name__ == '__main__':
    check_packages()
```

```bash
# Run verification
python check_requirements.py
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'X'**
   ```bash
   pip install X
   ```

2. **SSL Certificate Errors**
   ```bash
   pip install --upgrade pip certifi
   ```

3. **Permission Errors (Linux/macOS)**
   ```bash
   pip install --user -r requirements.txt
   ```

4. **Out of Memory**
   - Reduce concurrent scans
   - Increase system RAM
   - Use pagination for large results

5. **Rate Limit Errors**
   - Reduce attacks per vulnerability
   - Switch to provider with higher limits
   - Implement retry logic with backoff

---

**Last Updated**: February 2026  
**Python Version**: 3.10+  
**Core Framework**: Streamlit 1.32+, FastAPI 0.110+
