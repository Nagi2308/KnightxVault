# Use lightweight Python image
FROM python:3.9-slim

# Install build dependencies for tgcrypto & pymongo
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
    musl-dev \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY KnightxVaultreq.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot code
COPY Knightsxvault.py bot.py

# Run bot
CMD ["python", "bot.py"]
