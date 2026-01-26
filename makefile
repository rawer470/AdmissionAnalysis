SHELL := /bin/bash

# -------- Paths (repo-specific) --------
SLN        := AdmissionAnalysis.sln
WEB_CSPROJ := src/web/WebApp/WebApp.csproj
PY_DIR     := src/analysis

# -------- Python / venv --------
VENV   ?= .venv
PY     ?= $(VENV)/bin/python
PIP    ?= $(VENV)/bin/pip

# -------- Service config --------
API_HOST ?= 127.0.0.1
API_PORT ?= 8000
WEB_HOST ?= 127.0.0.1
WEB_PORT ?= 5002
WEB_URL  ?= http://localhost:5002

.PHONY: help venv py-install api test-api test-admission test-csv demo-summary \
        dotnet-restore dotnet-build web web-watch dev \
        analyze pdf clean

help:
	@echo ""
	@echo "Python:"
	@echo "  make venv            - create .venv"
	@echo "  make py-install      - install Python deps"
	@echo "  make api             - run FastAPI (uvicorn) with reload"
	@echo "  make test-api        - run API smoke tests (requires api running)"
	@echo "  make test-admission  - run AdmissionManager tests"
	@echo "  make test-csv        - run CSV demo script"
	@echo "  make demo-summary    - run demo_summary"
	@echo ""
	@echo "ASP.NET:"
	@echo "  make dotnet-restore  - dotnet restore"
	@echo "  make dotnet-build    - dotnet build"
	@echo "  make web             - dotnet run (WebApp)"
	@echo ""
	@echo "Combined:"
	@echo "  make dev             - run api + web in parallel"
	@echo ""
	@echo "API calls:"
	@echo "  make analyze DAY=03  - call /api/analyze/{DAY}"
	@echo "  make pdf             - call /api/generate_pdf_report"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - remove Python caches and dotnet bin/obj"
	@echo ""

# ---------------- Python ----------------

venv:
	@test -d "$(VENV)" || python3 -m venv $(VENV)

py-install: venv
	$(PIP) install -r $(PY_DIR)/requirements.txt
	$(PIP) install requests

api: py-install
	cd $(PY_DIR) && $(PY) -m uvicorn api_manager:app --host $(API_HOST) --port $(API_PORT) --reload

test-api: py-install
	$(PY) $(PY_DIR)/testLogic/test_api.py

test-admission:
	$(PY) $(PY_DIR)/testLogic/test_admission.py

test-csv:
	$(PY) $(PY_DIR)/testLogic/test_csv.py

demo-summary:
	$(PY) $(PY_DIR)/testLogic/demo_summary.py

# ---------------- ASP.NET ----------------

dotnet-restore:
	dotnet restore $(SLN)

dotnet-build:
	dotnet build $(SLN)

web: dotnet-restore
	ASPNETCORE_URLS=http://$(WEB_HOST):$(WEB_PORT) DOTNET_LAUNCH_PROFILE=http dotnet run --project $(WEB_CSPROJ)

# ---------------- Combined dev ----------------

dev:
	@echo "Starting API + Web in parallel..."
	@echo "API: http://$(API_HOST):$(API_PORT)  |  Web: $(WEB_URL)"
	@$(MAKE) -j2 api web

# ---------------- API helper calls ----------------

analyze:
	@if [ -z "$(DAY)" ]; then echo "Usage: make analyze DAY=03"; exit 1; fi
	$(PY) -c "import requests; print(requests.get('http://localhost:$(API_PORT)/api/analyze/$(DAY)').json())"

pdf:
	$(PY) -c "import requests; print(requests.get('http://localhost:$(API_PORT)/api/generate_pdf_report').json())"

# ---------------- Cleanup ----------------

clean:
	rm -rf $(VENV) .pytest_cache
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf src/web/**/bin src/web/**/obj src/web/bin src/web/obj