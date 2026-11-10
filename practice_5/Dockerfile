# syntax=docker/dockerfile:1

FROM python:3.12-slim

ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="MIIT Iris trainer" \
      org.opencontainers.image.description="Reproducible Iris training job" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models \
    MODEL_VERSION=1.0.0 \
    N_ESTIMATORS=100 \
    TEST_SIZE=0.3 \
    RANDOM_STATE=42

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --no-log-init --create-home appuser \
    && mkdir -p /app/models \
    && chown -R 10001:10001 /app

COPY --chown=10001:10001 train_model.py ./

USER 10001:10001

CMD ["python", "train_model.py"]
