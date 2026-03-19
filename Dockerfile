FROM python:3.11-slim
WORKDIR /app

# 🔥 install ffmpeg (THIS is the missing piece)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# copy code
COPY backend/ ./app

# copy requirements
COPY requirements.txt .

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]