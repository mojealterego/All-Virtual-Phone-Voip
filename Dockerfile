FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
RUN python -m pip install --no-cache-dir .

USER 65532:65532
EXPOSE 8080
CMD ["uvicorn", "avp.api:create_app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8080"]
