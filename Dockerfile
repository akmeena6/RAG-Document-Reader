# Base Image
FROM python:3.10-slim

# 1. Install System Dependencies (Tesseract for OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Set Work Directory to the project root inside the container
WORKDIR /project_root

# 3. Install Python Dependencies
# Copy requirements.txt from host root to container root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Source Code
# This copies the 'app' folder and config files into /project_root
COPY . .

# 5. Expose Port
EXPOSE 8501

# 6. Run Application
# CRITICAL CHANGE: We run the file located inside the 'app' folder
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]