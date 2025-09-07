FROM python:3.14-rc-alpine3.20

WORKDIR /app

# Install system dependencies using apk (Alpine package manager)
RUN apk update && \
    apk add --no-cache ffmpeg jq python3-dev gcc musl-dev libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Check yt-dlp dependency
RUN python3 -m pip check yt-dlp || true

CMD ["python3", "bot.py"]
