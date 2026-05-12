FROM python:3.12-slim

WORKDIR /app

# Install FFmpeg (required for audio extraction and merging)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

COPY . .

ENV DOWNLOAD_DIR=/app/Downloads
ENV CORS_ORIGINS=http://localhost:3000

RUN mkdir -p /app/Downloads

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]
