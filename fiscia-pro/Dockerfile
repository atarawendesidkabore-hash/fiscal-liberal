FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local
COPY fiscia ./fiscia
COPY data ./data
COPY alembic ./alembic
COPY alembic.ini ./
COPY requirements.txt ./

EXPOSE 8000
CMD ["uvicorn", "fiscia.app:app", "--host", "0.0.0.0", "--port", "8000"]

