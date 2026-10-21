FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 app
COPY pyproject.toml ./
COPY intel ./intel
COPY migrations ./migrations
COPY alembic.ini ./
RUN pip install --no-cache-dir . && mkdir -p /data/storage && chown -R app /data
USER app
ENV STORAGE_DIR=/data/storage
EXPOSE 8000
# Migrations run before the API starts; WORKER_IN_PROCESS=true runs research jobs in the same container.
CMD ["sh", "-c", "alembic upgrade head && uvicorn intel.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
