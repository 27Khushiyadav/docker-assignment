# ---- Stage 1: Builder ----
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libpq-dev

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---- Stage 2: Runtime ----
FROM python:3.11-alpine

WORKDIR /app

# Install only runtime dependency
RUN apk add --no-cache libpq

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY main.py .

# Create non-root user (security best practice)
RUN adduser -D appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]