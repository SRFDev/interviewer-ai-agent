# --- Stage 1: The "Builder" ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (if any needed for compiling)
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: The "Runner" ---
FROM python:3.12-slim AS runner

# Create a non-root user (Security Best Practice)
ARG UID=1001
ARG GID=1001
RUN groupadd --gid ${GID} appgroup && useradd --uid ${UID} --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy Application Code
# We copy the specific folders we need
COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup scripts ./scripts

# Set Environment for Streamlit
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Switch to non-root user
USER appuser

# Expose Cloud Run Port
EXPOSE 8080

# Run Command
CMD ["streamlit", "run", "app/ui.py"]

