# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY . .

# Create .streamlit directory and copy secrets
RUN mkdir -p /app/.streamlit
COPY frontend/.streamlit/secrets.toml /app/.streamlit/secrets.toml

EXPOSE 8501

CMD ["streamlit", "run", "frontend/main.py", "--server.address", "0.0.0.0", "--server.port", "8501"] 