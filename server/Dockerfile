FROM python:3.11-slim

WORKDIR /server

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    tini \
    bash \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install ipykernel

COPY requirements.txt .
COPY . .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]

