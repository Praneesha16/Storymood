# StoryMood API: FastAPI + ffmpeg (for mixing music under the narration).
# Build:  docker build -t storymood-api .
# Run:    docker run --env-file .env -p 8000:8000 storymood-api
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Music and generated files live outside the image in production (S3 + FILES_PROVIDER=s3);
# the folders exist so the local providers work inside the container too.
RUN mkdir -p static/audio static/images static/music data

ENV APP_ENV=production PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
