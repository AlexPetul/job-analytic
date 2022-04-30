FROM python:3.10-slim

COPY Pipfile /
RUN \
    apt-get update \
    && apt-get install -y gcc python3-dev \
    && pip install --upgrade pip setuptools-scm \
    && pip install pipenv \
    && pipenv lock -r > requirements.txt \
    && pip install --no-cache-dir -r /requirements.txt

COPY .. ./job_analytic

CMD ["uvicorn", "src.core.main:app", "--host", "0.0.0.0", "--port", "8000"]