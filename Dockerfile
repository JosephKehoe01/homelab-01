FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd -m appuser
WORKDIR /app

COPY scripts/ scripts/
COPY evidence/ evidence/
COPY samples/ samples/

RUN chown -R appuser:appuser /app
USER appuser

# Defaults (override at runtime)
ENV LOG_DIR=/var/log \
    OUT_PATH=/app/evidence/auth_failures.csv

ENTRYPOINT ["python", "scripts/parse_authlog.py"]
