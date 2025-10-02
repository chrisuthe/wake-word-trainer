FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    curl \
    build-essential \
    gcc \
    g++ \
    wget \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA toolkit for TensorFlow GPU training
# (Feature generation now happens in separate container with PyTorch)
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb && \
    dpkg -i cuda-keyring_1.1-1_all.deb && \
    apt-get update && \
    apt-get install -y \
        cuda-nvcc-12-0 \
        cuda-cudart-12-0 \
        cuda-cudart-dev-12-0 \
        libcudnn8 \
        libcublas-12-0 \
    && rm -rf /var/lib/apt/lists/* && \
    rm cuda-keyring_1.1-1_all.deb

# Set CUDA environment variables
ENV PATH="/usr/local/cuda-12.0/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda-12.0/lib64:${LD_LIBRARY_PATH}"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clone microWakeWord and piper-sample-generator repositories
RUN git clone https://github.com/kahrendt/microWakeWord.git /app/microWakeWord && \
    git clone https://github.com/rhasspy/piper-sample-generator.git /app/piper-sample-generator && \
    pip install --break-system-packages -e /app/microWakeWord

# Download default Piper voice models for sample generation
RUN mkdir -p /app/voices && \
    cd /app/voices && \
    curl -L -o en_US-lessac-medium.onnx 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true' && \
    curl -L -o en_US-lessac-medium.onnx.json 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true'

# Copy application files
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories for models and training jobs
RUN mkdir -p /app/models /app/training_jobs

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app/main.py
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app/main.py"]
