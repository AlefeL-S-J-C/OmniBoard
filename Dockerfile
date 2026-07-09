# -------------------------------------------------
# Build stage
# -------------------------------------------------
FROM python:3.12-slim AS builder
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -------------------------------------------------
# Production stage
# -------------------------------------------------
FROM python:3.12-slim AS production
WORKDIR /code
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:${PATH}"

COPY --from=builder /root/.local /root/.local
COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]