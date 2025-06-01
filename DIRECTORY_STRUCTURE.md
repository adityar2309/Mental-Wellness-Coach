# 📁 Mental Wellness Coach AI Agent Platform - Directory Structure

## 🏗️ Project Organization

This document describes the organized directory structure of the Mental Wellness Coach AI Agent Platform after reorganization for better maintainability and professional development practices.

## 📊 Directory Overview

```
Mental-Wellness-Coach/
├── 📂 backend/                    # Flask API backend service
│   ├── 📂 routes/                # API route handlers
│   ├── 📂 models/                # Database models
│   ├── 📂 services/              # Business logic services
│   ├── 📂 utils/                 # Utility functions
│   └── app.py                    # Main Flask application
│
├── 📂 mobile/                     # React Native mobile application
│   ├── 📂 src/                   # Source code
│   ├── 📂 components/            # React Native components
│   ├── 📂 screens/               # Mobile app screens
│   └── package.json              # Mobile dependencies
│
├── 🤖 agents/                     # Agentverse AI agents
│   ├── agentverse_conversation_coordinator.py  # Conversation management agent
│   └── agentverse_mood_tracker.py             # Mood tracking agent (deployed)
│
├── 🧪 tests/                      # Testing suite
│   ├── test_agentverse_agents.py # Agent unit tests
│   ├── test_all_features.py      # Comprehensive integration tests
│   ├── test_deployed_agent.py    # Live agent testing
│   └── test_requirements.txt     # Testing dependencies
│
├── 📚 docs/                       # Project documentation
│   ├── planning.md               # Architecture & development planning
│   ├── DEVELOPMENT.md            # Development setup guide
│   ├── TEST_README.md            # Testing documentation
│   ├── task.md                   # Task tracking & project management
│   ├── AGENTVERSE_DEPLOYMENT_GUIDE.md  # Agentverse deployment guide
│   └── GITHUB_DEPLOYMENT_SUCCESS.md    # Deployment success log
│
├── ⚙️ config/                     # Configuration files
│   └── env.example               # Environment variables template
│
├── 🚀 deployment/                 # Deployment configurations
│   └── docker-compose.yml        # Docker orchestration
│
├── 📝 scripts/                    # Utility scripts
│   └── demo_uagents.py           # uAgents demonstration script
│
├── 🐳 docker/                     # Docker configuration
│   ├── Dockerfile.backend        # Backend container
│   └── Dockerfile.mobile         # Mobile app container
│
├── 🔧 .github/                    # GitHub configuration
│   └── workflows/                # CI/CD workflows
│
├── 📄 Core Files
│   ├── README.md                 # Main project documentation
│   ├── requirements.txt          # Python dependencies
│   ├── package.json             # Node.js dependencies
│   ├── .gitignore               # Git ignore rules
│   └── .env                     # Environment variables (local)
│
└── 🗂️ Generated Folders
    ├── node_modules/             # Node.js packages
    ├── __pycache__/             # Python cache
    └── .pytest_cache/           # Pytest cache
```

## 📋 Directory Descriptions

### 🏭 **Backend** (`/backend/`)
- **Purpose**: Flask-based REST API server
- **Contents**: API routes, database models, business logic services
- **Key Features**: ASI:One LLM integration, SQLite database, JWT authentication
- **Port**: 3000 (development)

### 📱 **Mobile** (`/mobile/`)
- **Purpose**: React Native cross-platform mobile application
- **Contents**: Mobile UI components, screens, navigation
- **Key Features**: Mood tracking, crisis detection, offline support
- **Platforms**: iOS & Android

### 🤖 **Agents** (`/agents/`)
- **Purpose**: Autonomous AI agents for Agentverse platform
- **Contents**: Standalone agent scripts for deployment
- **Key Features**: 
  - **Mood Tracker**: Live on Agentverse (`agent1qtv48wjwflhu0mk5wev5jft5nlngtd84tpvjt6ckv63ynncjpfckj5xss8q`)
  - **Conversation Coordinator**: Ready for deployment

### 🧪 **Tests** (`/tests/`)
- **Purpose**: Comprehensive testing suite
- **Contents**: Unit tests, integration tests, live agent tests
- **Coverage**: 100% test coverage achieved
- **Framework**: Pytest with async support

### 📚 **Docs** (`/docs/`)
- **Purpose**: Project documentation and planning
- **Contents**: Architecture docs, deployment guides, task tracking
- **Key Files**:
  - `planning.md`: Project architecture & constraints
  - `task.md`: Development task tracking
  - `AGENTVERSE_DEPLOYMENT_GUIDE.md`: Step-by-step deployment

### ⚙️ **Config** (`/config/`)
- **Purpose**: Configuration templates and settings
- **Contents**: Environment variable templates, configuration files
- **Security**: No sensitive data stored in repository

### 🚀 **Deployment** (`/deployment/`)
- **Purpose**: Production deployment configurations
- **Contents**: Docker Compose, Kubernetes configs, deployment scripts
- **Environments**: Development, staging, production

### 📝 **Scripts** (`/scripts/`)
- **Purpose**: Utility and demonstration scripts
- **Contents**: Setup scripts, demos, maintenance tools
- **Usage**: Development automation and testing

## 🔄 File Organization Benefits

### ✅ **Improved Maintainability**
- Clear separation of concerns
- Easy navigation for developers
- Logical grouping of related files

### ✅ **Professional Structure**
- Industry-standard organization
- Scalable architecture
- Clear documentation hierarchy

### ✅ **Development Efficiency**
- Quick file location
- Consistent naming conventions
- Organized dependency management

### ✅ **Deployment Readiness**
- Separated environment configs
- Clear deployment documentation
- Containerized components

## 🚀 Quick Navigation

| Need to...                    | Go to...                        |
|-------------------------------|--------------------------------|
| 🔧 Modify API                | `/backend/`                    |
| 📱 Update mobile UI          | `/mobile/src/`                 |
| 🤖 Deploy new agents         | `/agents/`                     |
| 🧪 Run tests                 | `/tests/`                      |
| 📖 Read documentation        | `/docs/`                       |
| ⚙️ Configure environment     | `/config/`                     |
| 🚀 Deploy application        | `/deployment/`                 |

## 🎯 Next Steps

1. **Update import paths** in any scripts that reference moved files
2. **Update CI/CD workflows** to reflect new structure
3. **Create environment-specific configs** in `/config/`
4. **Add automated deployment scripts** to `/scripts/`
5. **Update mobile app** to use organized backend structure

---

*This structure follows industry best practices and supports the project's growth from prototype to production-ready mental health platform.* 