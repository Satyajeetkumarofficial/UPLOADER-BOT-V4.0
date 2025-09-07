FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (for ffmpeg, yt-dlp, pymongo, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg jq python3-dev gcc libffi-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Start the bot
CMD ["python3", "bot.py"]
