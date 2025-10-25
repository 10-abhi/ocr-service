FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#tesseract & req tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

#python dependencies
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

#application code copy
COPY . /app

#point pytesseract to tesseract binary(i am already setting this in my code on main and it is optional)
ENV TESSERACT_CMD=/usr/bin/tesseract

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
