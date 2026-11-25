# Use a small Python 3.12 base image for a reproducible API runtime.
FROM python:3.12-slim

# Keep application imports and relative paths stable inside the container.
WORKDIR /app

# Avoid bytecode artifacts and ensure application logs are emitted immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy dependency metadata first so repeated builds can reuse the install layer.
COPY requirements.txt .
COPY wheelhouse/ /wheelhouse/

# Install the pinned packages only from the repository's local wheelhouse.
RUN python -m pip install \
    --no-cache-dir \
    --no-index \
    --find-links=/wheelhouse \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]