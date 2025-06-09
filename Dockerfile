FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema para playwright
RUN apt-get update && \
    apt-get install -y wget gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libxshmfence1 libcurl4 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps

COPY . .

CMD ["python", "main.py"]