# BIST - BDD Intelligent Self-healing Tests

## Installation

### Quick Install
```bash
pip install -r requirements.txt
playwright install chromium
```

### From Source
```bash
git clone https://github.com/yourusername/bist.git
cd bist
pip install -e .
```

---

## Requirements

### requirements.txt
```
# Core dependencies
playwright==1.49.0
anthropic==0.43.0
click==8.1.7

# Optional: PostgreSQL support
psycopg2-binary==2.9.9

# Development
pytest==7.4.3
pytest-asyncio==0.23.0
black==23.12.0
```

### requirements-dev.txt
```
# All production deps
-r requirements.txt

# Additional dev tools
mypy==1.7.1
ruff==0.1.8
coverage==7.3.3
```

---

## setup.py

```python
from setuptools import setup, find_packages

with open("BIST_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bist-agent",
    version="0.1.0",
    author="QA Lab",
    author_email="contact@qalab.dev",
    description="AI-powered test automation agent. Open source alternative to QA.tech",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bist",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "playwright>=1.49.0",
        "anthropic>=0.43.0",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.0",
            "black>=23.12.0",
            "mypy>=1.7.1",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "bist=bist:cli",
        ],
    },
)
```

---

## Project Structure

```
bist/
├── README.md                      # Main documentation
├── LICENSE                        # MIT License
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package configuration
├── .gitignore                     # Git ignore rules
│
├── bist.py                        # CLI entry point
├── bist_agent.py                  # Core agent (formerly qalab_agent_core.py)
├── bist_orchestrator.py           # Test orchestration
├── bist_database.py               # Database layer
├── bist_parser.py                 # Gherkin parser
│
├── examples/                      # Example user stories and tests
│   ├── login.md
│   ├── checkout.md
│   └── README.md
│
├── tests/                         # Test suite
│   ├── test_agent.py
│   ├── test_parser.py
│   └── test_database.py
│
├── docs/                          # Documentation
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── ci-cd-guide.md
│   └── monetization-guide.md
│
├── .github/
│   └── workflows/
│       ├── tests.yml              # Run test suite
│       ├── bist-demo.yml          # Demo workflow
│       └── release.yml            # Package release
│
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── .dockerignore
```

---

## Environment Setup

### .env.example
```bash
# Anthropic API Key (required)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/bist

# Test Environment (optional)
DEFAULT_TEST_ENV=https://staging.myapp.com

# Concurrency (optional)
BIST_MAX_PARALLEL=3

# Playwright (optional)
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```

---

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy application
COPY . .

# Create volume for test results
VOLUME ["/app/test-results"]

# Entry point
CMD ["python", "bist.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  bist:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://bist:bist@postgres:5432/bist
    volumes:
      - ./test-results:/app/test-results
      - ./features:/app/features
      - ./stories:/app/stories
    depends_on:
      - postgres
    command: >
      python bist.py full
      --user-story /app/stories/example.md
      --feature /app/features/example.feature
      --env https://staging.example.com

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: bist
      POSTGRES_USER: bist
      POSTGRES_PASSWORD: bist
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

## CI/CD Examples

### GitHub Actions

```yaml
# .github/workflows/bist-tests.yml
name: BIST Tests

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install BIST
        run: |
          pip install -r requirements.txt
          playwright install chromium --with-deps
      
      - name: Run Tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python bist.py full \
            --user-story stories/critical.md \
            --feature tests/critical.feature \
            --env ${{ secrets.STAGING_URL }}
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: bist-results
          path: test-results/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
bist-tests:
  image: python:3.11
  
  before_script:
    - pip install -r requirements.txt
    - playwright install chromium --with-deps
  
  script:
    - python bist.py full
        --user-story stories/critical.md
        --feature tests/critical.feature
        --env $STAGING_URL
  
  artifacts:
    when: always
    paths:
      - test-results/
    expire_in: 30 days
```

---

## First Run

```bash
# 1. Clone and install
git clone https://github.com/yourusername/bist.git
cd bist
pip install -r requirements.txt
playwright install chromium

# 2. Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key"

# 3. Try the example
python bist.py full \
  --user-story examples/login.md \
  --feature tests/login.feature \
  --env https://demo.playwright.dev

# 4. Check results
open test-results/report.html
```

**Expected output:**
```
🎯 Pipeline Completo: User Story → BDD → Execution

Step 1: Gerando cenários BDD...
🤖 Gerando cenários para: User Login
✓ Qualidade atingida: 0.85
✓ Cenários salvos em: tests/login.feature

Step 2: Executando testes...
🧪 Executando: Login with valid credentials
   [1/5] Navigate to login page... ✓ PASSED (2.1s)
   [2/5] Fill email field... ✓ PASSED (0.8s)
   [3/5] Fill password field... ✓ PASSED (0.7s)
   [4/5] Click Sign In button... ✓ PASSED (1.2s)
   [5/5] Verify dashboard... ✓ PASSED (0.9s)

📊 Resultados:
   ✅ Passed: 1/1
   ⏱️  Duration: 5.7s

📄 Relatório: test-results/report.html

✅ Pipeline completo!
```

---

## Troubleshooting

### Issue: "playwright not found"
```bash
# Solution
playwright install chromium --with-deps
```

### Issue: "Anthropic API error"
```bash
# Check your API key
echo $ANTHROPIC_API_KEY

# Or set it
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Issue: "Tests are slow"
```bash
# Run in parallel
python bist.py execute --feature tests/*.feature --parallel
```

### Issue: "Flaky tests"
```bash
# Check flaky detection
python bist.py stats

# See history
sqlite3 bist.db "SELECT * FROM test_results WHERE scenario_name LIKE '%your_test%'"
```

---

## Next Steps

1. ✅ **Run the example** (above)
2. 📝 **Write your first User Story** (see `examples/`)
3. 🚀 **Generate and execute** with BIST
4. 🔁 **Integrate with CI/CD** (GitHub Actions)
5. 📊 **Monitor with dashboard** (coming soon)

---

**Welcome to BIST! 🎯**

**Questions? Open an issue or join our Discord.**
