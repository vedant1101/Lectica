FROM python:3.11-slim

WORKDIR /app

# 🔥 install ffmpeg (THIS is the missing piece)
RUN apt-get update && apt-get install -y ffmpeg

# copy code
COPY backend/ ./app

# install python deps
RUN pip install --no-cache-dir -r app/requirements.txt

# run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]