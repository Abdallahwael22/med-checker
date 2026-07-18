# ── Base image ────────────────────────────────────────────────
# Python 3.12 slim on Debian Bookworm — small but has apt-get
FROM python:3.12-slim-bookworm

# ── System dependencies ────────────────────────────────────────
# OpenCV needs these Linux libraries to run headlessly
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Install uv ────────────────────────────────────────────────
RUN pip install uv --no-cache-dir

# ── Working directory ─────────────────────────────────────────
WORKDIR /app

# ── Copy dependency files first (layer caching) ───────────────
# Copying only pyproject.toml first means Docker reuses this
# layer on rebuild if your code changes but deps don't
COPY pyproject.toml ./

# ── Remove Windows-only uv constraint ─────────────────────────
# The pyproject.toml has environments = ["sys_platform == 'win32'"]
# which breaks Linux. Remove it before installing.
RUN sed -i '/tool.uv/,/^\[/{ /environments/d }' pyproject.toml || true

# ── Install dependencies ───────────────────────────────────────
RUN uv pip install --system --no-cache \
    "langchain>=1.3.11" \
    "langchain-core>=1.4.8" \
    "langchain-groq>=1.1.3" \
    "langgraph>=1.2.7" \
    "langsmith>=0.9.7" \
    "opencv-python-headless>=4.6.0" \
    "paddleocr>=3.7.0" \
    "paddlepaddle>=3.3.1" \
    "pydantic>=2.13.4" \
    "pydantic-settings>=2.14.2" \
    "python-dotenv>=1.2.2" \
    "requests>=2.34.2" \
    "streamlit>=1.58.0" \
    "pillow>=9.0.0" \
    "setuptools>=83.0.0" \
    "numpy<2.0.0"

# ── Pre-download PaddleOCR models ─────────────────────────────
# Download models at build time so the container starts instantly
# without downloading on every first run
RUN python -c "\
from paddleocr import PaddleOCR; \
print('Downloading PaddleOCR models...'); \
PaddleOCR(use_textline_orientation=True); \
print('Models downloaded successfully') \
" || echo "Model pre-download skipped — will download on first run"

# ── Copy application code ──────────────────────────────────────
COPY src/ ./src/
COPY app/ ./app/
COPY data/patients/ ./data/patients/

# ── Environment variables ──────────────────────────────────────
# These are defaults — override at runtime via docker-compose or -e flag
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GROQ_API_KEY=""
ENV LANGSMITH_API_KEY=""
ENV LANGSMITH_TRACING=false
ENV LANGSMITH_PROJECT=med-checker

# ── Expose Streamlit port ──────────────────────────────────────
EXPOSE 8501

# ── Health check ──────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ── Entry point ────────────────────────────────────────────────
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
