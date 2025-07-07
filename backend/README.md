# Agentic Task Management System Backend

Backend Phase 1 implementation for the Agentic Pseudo system with FastAPI, PostgreSQL, and comprehensive CRUD operations.

## Overview

This system provides a robust backend API for managing agents, templates, conversations, and data units. It includes both the new PostgreSQL-based CRUD system and maintains backward compatibility with the existing task management functionality.

## System Architecture

### Key Components

#### New CRUD System (Phase 1)
- **FastAPI Framework**: High-performance async web framework
- **PostgreSQL Database**: Reliable relational database with async support
- **Layered Architecture**: Clean separation of concerns (API → Service → Repository)
- **JWT Authentication**: Secure token-based authentication
- **Comprehensive CRUD**: Full Create, Read, Update, Delete operations

#### Legacy Task Management System
- **Planner Agent**: Handles task decomposition, planning, and execution coordination
- **Sub-Agents**: Specialized task execution (Web, Coder, Casual, File Agents)
- **KVS (Upstash)**: Persistent storage for hearing results, task schemas, and task data

### Architecture Diagram

```mermaid
graph TD
    User[User] -->|Task Instructions| API[REST API]
    API -->|Task Request| PlannerAgent[Planner Agent]
    PlannerAgent -->|Task Planning/Execution| SubAgents[Sub-Agents]
    PlannerAgent -->|Data Storage/Reference| KVS[KVS Upstash]
    SubAgents -->|Execution Results| PlannerAgent
    KVS -->|Schema/Data| PlannerAgent
```

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI, Pydantic v2
- **Database**: PostgreSQL (with AsyncPG), Upstash Redis (legacy)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT)
- **LLM**: DSPy (Gemini Flash 2.5) - legacy system
- **Package Management**: uv
- **Code Quality**: Ruff, Pyright

## Setup

### Prerequisites

- Python 3.11 or higher
- uv (Python package manager)

### Installation

```bash
# Clone the project
git clone <repository-url>
cd agentic_pseudo

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env file to configure Upstash URL/TOKEN and LLM API keys
```

### Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_pseudo

# Authentication
SECRET_KEY=your-secret-key-here-change-this-in-production

# Legacy Redis Configuration (for existing KVS)
UPSTASH_REDIS_REST_URL=your-redis-url
UPSTASH_REDIS_REST_TOKEN=your-redis-token

# OpenAI Configuration (for LLM agents)
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your_gemini_api_key
```

## Usage

### Start API Server

```bash
uv run uvicorn src.api.main:app --reload
```

### Run Tests

```bash
# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run pyright

# Run tests
uv run pytest tests/acceptance/  # Acceptance tests
uv run pytest tests/integration/ # Integration tests
```

## API Endpoints

### New CRUD API (v1)

#### Agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent

#### Templates
- `POST /api/v1/templates/` - Create template
- `GET /api/v1/templates/` - List templates
- `GET /api/v1/templates/{id}` - Get template
- `PUT /api/v1/templates/{id}` - Update template
- `DELETE /api/v1/templates/{id}` - Delete template

#### Conversations
- `POST /api/v1/conversations/` - Create conversation
- `GET /api/v1/conversations/` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation
- `PUT /api/v1/conversations/{id}` - Update conversation
- `DELETE /api/v1/conversations/{id}` - Delete conversation
- `POST /api/v1/conversations/{id}/messages` - Add message
- `GET /api/v1/conversations/{id}/messages` - Get messages

#### Data Units
- `POST /api/v1/data-units/` - Create data unit
- `GET /api/v1/data-units/` - List data units
- `GET /api/v1/data-units/{id}` - Get data unit
- `PUT /api/v1/data-units/{id}` - Update data unit
- `DELETE /api/v1/data-units/{id}` - Delete data unit

### Legacy Task Management API

#### Create Task
```http
POST /api/tasks/create
{
  "user_instruction": "Please collect information for report creation and then create the report",
  "session_id": "optional-session-id"
}
```

#### Save Hearing Results
```http
POST /api/hearing
{
  "session_id": "session-uuid",
  "hearing_result": "User's detailed requirements and configuration information"
}
```

#### Get Task Status
```http
GET /api/tasks/status/{session_id}
```

## Project Structure

```
src/
├── api/                    # FastAPI routers and endpoints
│   ├── main.py            # Main FastAPI application
│   ├── agents.py          # Agent endpoints
│   ├── templates.py       # Template endpoints
│   ├── conversations.py   # Conversation/Message endpoints
│   └── data_units.py      # Data unit endpoints
├── service/               # Business logic layer
│   ├── agent_service.py
│   ├── template_service.py
│   ├── conversation_service.py
│   ├── data_unit_service.py
│   └── ... (legacy agents)
├── models/                # Data models
│   ├── database_models.py # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── task_models.py     # Legacy task models
├── repository/            # Data access layer (KVS operations - legacy)
├── database.py           # Database configuration
├── auth.py               # Authentication utilities
└── exceptions.py         # Custom exceptions

tests/
├── acceptance/    # Acceptance tests
├── integration/   # Integration tests
└── unit/          # Unit tests

alembic/           # Database migrations
output/            # Generated artifacts and reports directory
docs/              # Design documents
```

## Key Features

### New CRUD System (Phase 1)
- **Comprehensive CRUD Operations**: Full Create, Read, Update, Delete for all entities
- **Async Database Operations**: High-performance async PostgreSQL integration
- **JWT Authentication**: Secure token-based authentication system
- **Input Validation**: Comprehensive Pydantic validation with security focus
- **Database Migrations**: Alembic for schema version management
- **Testing**: Comprehensive test coverage with SQLite in-memory testing
- **Serverless Ready**: Optimized for Vercel deployment with Neon PostgreSQL

### Legacy Task Management System
- **Task Decomposition and Execution Planning**: Decomposes user instructions into structured tasks
- **Agent Collaboration**: Web, Coder, Casual, and File specialized agents
- **KVS Integration**: Persistent storage using Upstash Redis

## Development Philosophy

- **Test-Driven Development**: Focus on acceptance and integration tests
- **Security First**: Input validation and sensitive information protection
- **Layered Design**: API → Service → Repository → Model
- **Type Safety**: Strict type definitions using Pydantic v2

## License

MIT License