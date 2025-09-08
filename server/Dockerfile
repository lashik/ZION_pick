# Dockerfile: Production-Ready, Final Version

# Start from the official Python 3.9 slim base image.
FROM python:3.9-slim

# Set the main working directory inside the container.
WORKDIR /app

# --- Install ALL System-Level Dependencies (Layer 1) ---
RUN apt-get update && apt-get install -y \
    # Core essentials
    build-essential \
    git \
    # Process manager
    supervisor \
    # Multimedia and graphics libraries required by OpenCV
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    # Libraries for handling image formats
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # Libraries for handling video codecs
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # Other common CV dependencies
    libgtk2.0-dev \
    redis-tools \
    # Clean up apt cache to keep image size smaller
    && rm -rf /var/lib/apt/lists/*

# Copy the Python requirements file.
COPY requirements.txt .

# --- Install ALL Python-Level Dependencies (Layer 2) ---
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code and assets.
COPY app/ .
COPY models/ ./models/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set the final command to start supervisor.
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
