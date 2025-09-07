FROM python:3.11-slim

WORKDIR /app

# Dependencies install
RUN apt-get update && \
    apt-get install -y ffmpeg jq python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Requirements install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run bot
CMD ["python", "bot.py"]
