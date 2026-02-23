FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip pdm

WORKDIR /app

# Copy only lockfiles first to leverage Docker cache
COPY pyproject.toml pdm.lock /app/

# Export requirements (including dev to get uvicorn) and install
RUN python -m pdm export -f requirements --dev -o requirements.txt && \
    pip install -r requirements.txt

# Copy project
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
