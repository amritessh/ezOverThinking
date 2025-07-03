

set -e  # Exit on any error

echo "🚀 Setting up ezOverThinking Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on macOS, Linux, or Windows
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_info "Detected OS: ${MACHINE}"

# Check Prerequisites
echo -e "\n${BLUE}📋 Checking Prerequisites...${NC}"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python ${PYTHON_VERSION} found"
else
    print_error "Python 3.11+ is required but not found"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker ${DOCKER_VERSION} found"
else
    print_error "Docker is required but not found"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose ${COMPOSE_VERSION} found"
else
    print_error "Docker Compose is required but not found"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_status "Git ${GIT_VERSION} found"
else
    print_error "Git is required but not found"
    exit 1
fi

# Step 1: Create Project Structure
echo -e "\n${BLUE}📁 Creating Project Structure...${NC}"

# Create main directories
mkdir -p src/{agents,models,services,tools,utils,config}
mkdir -p api/{endpoints,middleware}
mkdir -p frontend/{components,static}
mkdir -p docs
mkdir -p scripts
mkdir -p monitoring/{docker,grafana/dashboards}

# Create __init__.py files
find src api frontend -type d -exec touch {}/__init__.py \;

print_status "Project structure created"

# Step 2: Create Virtual Environment
echo -e "\n${BLUE}🐍 Setting up Python Virtual Environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Step 3: Install Dependencies
echo -e "\n${BLUE}📦 Installing Python Dependencies...${NC}"

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing basic dependencies"
    pip install fastapi uvicorn streamlit redis psycopg2-binary
fi

# Step 4: Environment Configuration
echo -e "\n${BLUE}⚙️  Setting up Environment Configuration...${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Created .env file from .env.example"
        print_warning "Please edit .env file with your API keys and configuration"
    else
        # Create basic .env file
        cat > .env << EOF
# ezOverThinking Environment Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
LANGCHAIN_API_KEY=your_langchain_key_here

DATABASE_URL=postgresql://ezuser:ezpassword@localhost:5432/ezoverthinking
REDIS_URL=redis://localhost:6379/0

ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your_super_secret_key_here
EOF
        print_status "Created basic .env file"
    fi
else
    print_warning ".env file already exists"
fi

# Step 5: Docker Services Setup
echo -e "\n${BLUE}🐳 Setting up Docker Services...${NC}"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create docker-compose.yml if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
    print_warning "docker-compose.yml not found, creating basic configuration"
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ezoverthinking
      POSTGRES_USER: ezuser
      POSTGRES_PASSWORD: ezpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
EOF
fi

# Start Docker services
print_info "Starting Docker services..."
docker-compose up -d redis postgres

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Test Redis connection
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    print_status "Redis is ready"
else
    print_warning "Redis might not be ready yet"
fi

# Test PostgreSQL connection
if docker-compose exec -T postgres pg_isready -U ezuser -d ezoverthinking &> /dev/null; then
    print_status "PostgreSQL is ready"
else
    print_warning "PostgreSQL might not be ready yet"
fi

# Step 6: Code Quality Setup
echo -e "\n${BLUE}🔍 Setting up Code Quality Tools...${NC}"

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_status "Pre-commit hooks installed"
else
    print_warning "pre-commit not found, skipping hook installation"
fi

# Create .pre-commit-config.yaml if it doesn't exist
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
EOF
    print_status "Created .pre-commit-config.yaml"
fi

# Step 7: Documentation Setup
echo -e "\n${BLUE}📚 Setting up Documentation...${NC}"

# Create basic README if it doesn't exist
if [ ! -f "README.md" ]; then
    cat > README.md << EOF
# ezOverThinking

A sophisticated multi-agent AI system that humorously escalates anxiety through coordinated AI agent interactions.

## Features

- **Multi-Agent System**: 6 distinct AI agents with unique personalities
- **Real-time State Management**: Redis-based conversation state tracking
- **Scalable Architecture**: Microservices-ready design
- **Interactive Demo**: Streamlit-based user interface
- **Production Ready**: Docker containerization and monitoring

## Quick Start

1. Clone the repository
2. Run setup script: \`./scripts/setup_dev_environment.sh\`
3. Start services: \`docker-compose up -d\`
4. Run the API: \`uvicorn api.main:app --reload\`
5. Access demo: \`streamlit run frontend/streamlit_app.py\`

## Architecture

- **FastAPI**: High-performance API backend
- **Streamlit**: Interactive frontend
- **Redis**: Real-time state management
- **PostgreSQL**: Persistent data storage
- **LangChain**: AI agent orchestration
- **CrewAI**: Multi-agent coordination

## Development

\`\`\`bash
# Setup development environment
./scripts/setup_dev_environment.sh

# Start development services
docker-compose up -d

# Run API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend
streamlit run frontend/streamlit_app.py
\`\`\`

## License

MIT License
EOF
    print_status "Created README.md"
fi

# Step 8: Create basic project files
echo -e "\n${BLUE}📄 Creating Basic Project Files...${NC}"

# Create .gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json
EOF
    print_status "Created .gitignore"
fi

# Create pyproject.toml
if [ ! -f "pyproject.toml" ]; then
    cat > pyproject.toml << EOF
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ezoverthinking"
version = "0.1.0"
description = "A sophisticated multi-agent AI system for humorous anxiety escalation"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_any_generics = true
disallow_untyped_defs = true
follow_imports = "silent"
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_unimported = true
no_implicit_optional = true
warn_return_any = true
warn_unused_configs = true
EOF
    print_status "Created pyproject.toml"
fi

# Step 9: Health Check
echo -e "\n${BLUE}🏥 Running Health Checks...${NC}"

# Check Python environment
if python3 -c "import sys; print(f'Python {sys.version}')" &> /dev/null; then
    print_status "Python environment is working"
else
    print_error "Python environment has issues"
fi

# Check Docker services
if docker-compose ps | grep -q "Up"; then
    print_status "Docker services are running"
else
    print_warning "Some Docker services may not be running"
fi

# Step 10: Final Instructions
echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Edit .env file with your API keys:"
echo "   - OPENAI_API_KEY"
echo ""
echo "2. Start the development server:"
echo "   ${YELLOW}uvicorn api.main:app --reload${NC}"
echo ""
echo "3. In another terminal, start the frontend:"
echo "   ${YELLOW}streamlit run frontend/streamlit_app.py${NC}"
echo ""
echo "4. Access the application:"
echo "   - API: http://localhost:8000"
echo "   - Frontend: http://localhost:8501"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "5. Monitor services:"
echo "   - Redis: localhost:6379"
echo "   - PostgreSQL: localhost:5432"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"

# Make the script executable
