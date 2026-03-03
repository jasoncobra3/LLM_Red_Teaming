# Architecture Documentation

## System Overview

The LLM Red Teaming Platform is a comprehensive security testing framework designed to evaluate Large Language Models (LLMs) against adversarial attacks, jailbreaks, and security vulnerabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
├──────────────────────┬──────────────────────────────────────────┤
│   Streamlit UI       │         FastAPI Web App                  │
│   (app.py)           │         (web_app.py)                     │
│   - Dashboard        │         - REST API                       │
│   - Attack Lab       │         - HTML Templates                 │
│   - Results View     │         - Real-time Updates              │
│   - Reports          │         - Session Management             │
└──────────────────────┴──────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Business Logic                         │
├──────────────────────┬─────────────────────┬────────────────────┤
│  Red Team Engine     │   LLM Factory       │  Attack Registry   │
│  (red_team_engine)   │   (llm_factory)     │  (attack_registry) │
│                      │                     │                    │
│  - Scan Orchestration│   - Model Creation  │  - Vulnerabilities │
│  - Attack Execution  │   - Provider Setup  │  - Attack Methods  │
│  - Result Parsing    │   - DeepEval Adapter│  - Frameworks      │
└──────────────────────┴─────────────────────┴────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   DeepTeam      │  │  LangChain   │  │  Attack Library  │
│   Framework     │  │  Integration │  │  (attack_library)│
│                 │  │              │  │                  │
│  - Vulnerability│  │  - Chat      │  │  - Predefined    │
│    Testing      │  │    Models    │  │    Prompts       │
│  - Attack       │  │  - Providers │  │  - Jailbreaks    │
│    Enhancement  │  │              │  │  - Categories    │
└─────────────────┘  └──────────────┘  └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data & Infrastructure Layer                  │
├──────────────────────┬─────────────────────┬────────────────────┤
│   Database Layer     │   Configuration     │   Utilities        │
│   (database/)        │   (config/)         │   (utils/)         │
│                      │                     │                    │
│  - SQLite DB         │  - Settings         │  - Logging         │
│  - Models (ORM)      │  - Providers        │  - Helpers         │
│  - DB Manager        │  - Environment      │  - Validators      │
└──────────────────────┴─────────────────────┴────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### Streamlit UI (`app.py`)
- **Purpose**: Interactive dashboard for security researchers
- **Key Features**:
  - Multi-page navigation (Dashboard, Configure, Attack Lab, Results, Reports)
  - Real-time scan monitoring
  - Visual analytics and charts
  - PDF report generation
- **Technology**: Streamlit 1.x

#### FastAPI Web App (`web_app.py`)
- **Purpose**: RESTful API and HTML-based interface
- **Key Features**:
  - Authentication middleware
  - Background task management
  - Real-time scan status updates
  - Template-based rendering (Jinja2)
- **Endpoints**:
  - `/api/scan` - Initiate red team scans
  - `/api/results/{scan_id}` - Retrieve scan results
  - `/api/reports/{scan_id}` - Generate PDF reports
  - `/api/providers` - Get configured LLM providers

### 2. Core Business Logic

#### Red Team Engine (`core/red_team_engine.py`)
```python
Key Functions:
├── run_red_team_scan()
│   ├── Model creation and configuration
│   ├── DeepTeam scan orchestration
│   ├── Result parsing and filtering
│   └── Database persistence
│
├── _parse_risk_assessment()
│   ├── Extract test cases
│   ├── Parse vulnerability scores
│   └── Format results
│
└── _extract_test_case()
    ├── Pydantic model extraction
    ├── Multi-attribute fallback
    └── Error handling
```

**Key Responsibilities**:
- Orchestrates vulnerability scans
- Manages attacker and target models
- Filters rate-limited/failed tests
- Persists results to database

#### LLM Factory (`core/llm_factory.py`)
```python
create_deepeval_model()
    ├── Provider selection (OpenAI, Azure, Groq, etc.)
    ├── Model configuration (temperature, tokens)
    ├── LangChain model creation
    └── DeepEvalBaseLLM adapter wrapping
```

**LangChainAdapter**:
- Wraps LangChain models for DeepTeam compatibility
- Detects JSON mode support (OpenAI/Azure)
- Handles schema-based generation
- Manages async operations

#### Attack Registry (`core/attack_registry.py`)
- **Vulnerabilities**: 7+ categories (Robustness, Indirect Injection, etc.)
- **Attacks**: 12+ methods (Jailbreak, Prompt Leaking, ROT13, etc.)
- **Frameworks**: OWASP LLM Top 10, NIST AI RMF

### 3. Integration Layer

#### DeepTeam Framework
- **Purpose**: Core red teaming engine
- **Capabilities**:
  - Automated attack generation
  - Multi-turn conversations
  - Risk assessment scoring
  - Vulnerability classification

#### LangChain Integration
- **Purpose**: Unified LLM interface
- **Supported Providers**:
  - OpenAI (GPT-4, GPT-3.5)
  - Azure OpenAI
  - Groq (Llama 3.x, Mixtral)
  - Anthropic Claude
  - Google Gemini
  - Local models (Ollama)

### 4. Data Layer

#### Database Schema
```sql
-- Scans table
scans (
    scan_id TEXT PRIMARY KEY,
    target_model TEXT,
    attacker_model TEXT,
    status TEXT,
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    overall_score REAL,
    created_at TIMESTAMP
)

-- Results table
results (
    result_id INTEGER PRIMARY KEY,
    scan_id TEXT,
    vulnerability_type TEXT,
    attack_type TEXT,
    input_prompt TEXT,
    target_response TEXT,
    score REAL,
    passed BOOLEAN,
    reason TEXT,
    FOREIGN KEY(scan_id) REFERENCES scans(scan_id)
)
```

## Data Flow

### Red Team Scan Execution Flow
```
1. User initiates scan
   └─> Configure: target model, attacker model, vulnerabilities

2. UI submits request
   └─> app.py (Streamlit) OR web_app.py (FastAPI)

3. Red Team Engine processing
   ├─> Create models via LLM Factory
   │   ├─> LangChain model instantiation
   │   └─> DeepEval adapter wrapping
   │
   ├─> Initialize DeepTeam scanner
   │   ├─> Load vulnerabilities & attacks
   │   └─> Configure async execution
   │
   ├─> Execute attacks
   │   ├─> Attacker generates malicious prompts
   │   ├─> Target model responds
   │   └─> Evaluator scores responses
   │
   └─> Parse & filter results
       ├─> Extract test cases
       ├─> Filter rate-limited failures
       └─> Calculate metrics

4. Persist to database
   └─> SQLite via db_manager

5. Display results
   └─> UI refreshes with scan status
```

### Model Interaction Flow
```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Attacker   │──────>│   Target     │──────>│  Evaluator   │
│   Model      │       │   Model      │       │   Model      │
└──────────────┘       └──────────────┘       └──────────────┘
      │                      │                       │
      │                      │                       │
   Generate              Respond                 Score
   Attack                to                      Response
   Prompt                Attack                  (0-1)
      │                      │                       │
      └──────────────────────┴───────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Test Case      │
                    │  - Input        │
                    │  - Output       │
                    │  - Score        │
                    │  - Judgment     │
                    └─────────────────┘
```

## Security Architecture

### Authentication Flow
```
1. User access
   └─> Check session

2. If not authenticated
   ├─> Redirect to login
   └─> Validate credentials

3. On success
   ├─> Create session token
   └─> Store in session manager

4. Subsequent requests
   └─> Middleware validates token
```

### API Key Management
- Environment variables (`.env`)
- Never logged or exposed
- Encrypted at rest (future enhancement)

## Scalability Considerations

### Current Limitations
- Single-server deployment
- Synchronous scan execution
- SQLite database (not suitable for high concurrency)

### Future Enhancements
1. **Distributed Scanning**: Celery + Redis task queue
2. **Database Upgrade**: PostgreSQL for production
3. **Caching Layer**: Redis for scan results
4. **Load Balancing**: Multiple API servers
5. **Async Everything**: Full async/await implementation

## Technology Stack

### Backend
- **Python 3.10+**: Core language
- **FastAPI**: REST API framework
- **Streamlit**: Dashboard UI
- **SQLAlchemy**: ORM (future)
- **Pydantic**: Data validation

### ML/AI
- **DeepTeam**: Red teaming framework
- **LangChain**: LLM orchestration
- **OpenAI SDK**: GPT models
- **Anthropic SDK**: Claude models

### Database
- **SQLite**: Development database
- **PostgreSQL**: Production (recommended)

### DevOps
- **Uvicorn**: ASGI server
- **Docker**: Containerization (future)
- **GitHub Actions**: CI/CD (future)

## Deployment Architecture

### Development
```
Local Machine
├── Python virtual environment
├── SQLite database
├── .env configuration
└── Streamlit/FastAPI server
```

### Production (Recommended)
```
┌────────────────────────────────────────┐
│           Load Balancer (nginx)        │
└────────────────┬───────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  App    │  │  App    │  │  App    │
│ Server  │  │ Server  │  │ Server  │
│   #1    │  │   #2    │  │   #3    │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  ▼
         ┌─────────────────┐
         │   PostgreSQL    │
         │    Database     │
         └─────────────────┘
                  │
         ┌─────────────────┐
         │   Redis Cache   │
         └─────────────────┘
```

## Monitoring & Logging

### Logging Strategy
- **File-based**: `logs/red_teaming.log`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: Daily (future enhancement)

### Metrics to Track
- Scans per day
- Success/failure rates
- Average scan duration
- Model API costs
- Rate limit occurrences

## Error Handling

### Error Categories
1. **Rate Limits**: Detected and filtered
2. **JSON Errors**: Fallback mechanisms
3. **API Failures**: Retry logic
4. **Database Errors**: Transaction rollback

### Recovery Mechanisms
- Graceful degradation
- Error filtering (rate limits excluded from results)
- User-friendly error messages
- Detailed logging for debugging

## Configuration Management

### Environment Variables
```env
OPENAI_API_KEY=...
GROQ_API_KEY=...
AZURE_OPENAI_KEY=...
SECRET_KEY=...
DATABASE_URL=sqlite:///red_teaming.db
LOG_LEVEL=INFO
```

### Provider Configuration
- Dynamic provider registration
- Model capability detection
- Automatic fallback selection

---

**Last Updated**: February 2026  
**Version**: 1.0.0
