# Wake Word Trainer for Home Assistant 🎙️

A GPU-accelerated web application for training custom wake words for Home Assistant and ESPHome devices. Generate lightweight TensorFlow Lite models optimized for ESP32-S3 microcontrollers using MicroWakeWord.

![Wake Word Trainer Interface](https://img.shields.io/badge/Platform-Docker-2496ED?style=for-the-badge&logo=docker)
![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![CUDA](https://img.shields.io/badge/CUDA-12.0-76B900?style=for-the-badge&logo=nvidia)

## ✨ Features

- 🎙️ **Custom Wake Words** - Train personalized wake words for Home Assistant
- 🚀 **GPU Accelerated** - Leverage NVIDIA GPU for fast training (CUDA 12.0)
- 🔬 **MicroWakeWord** - Generate lightweight models for ESP32-S3 devices
- 📱 **ESPHome Ready** - Download `.tflite` models ready for ESPHome
- 🌐 **Modern Web UI** - Clean, responsive interface with real-time progress
- 🔊 **Synthetic Samples** - Automatic sample generation using Piper TTS
- 📊 **Training History** - Track and manage multiple training jobs
- 🐳 **Docker Deployment** - Easy multi-container setup with Docker Compose
- 🏗️ **Microservices Architecture** - Separated PyTorch/TensorFlow to avoid conflicts

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **NVIDIA GPU** with CUDA support (RTX series or better recommended)
- **NVIDIA Container Toolkit** (nvidia-docker2) for GPU passthrough
- At least **8GB RAM** and **10GB disk space**

### Windows (WSL2) Setup

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Enable WSL2 backend in Docker Desktop settings
3. Install [NVIDIA CUDA on WSL2](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)
4. Verify GPU: `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi`

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/chrisuthe/wake-word-trainer.git
cd wake-word-trainer
```

### 2. Build and Start Services

```bash
docker-compose up -d --build
```

This starts two services:
- **wake-word-trainer**: Main web interface and training (port 5000)
- **feature-generator**: PyTorch-based feature extraction (port 5001)

### 3. Access the Web Interface

```
http://localhost:5000
```

### 4. Train Your First Wake Word

1. Enter wake word phrase (e.g., "hey betty", "okay assistant")
2. Select MicroWakeWord method
3. Choose preset or customize advanced settings
4. Click "Start Training"
5. Monitor real-time progress
6. Download `.tflite` model when complete

## 🏗️ Architecture

Microservices architecture to avoid PyTorch/TensorFlow CUDA conflicts:

```
┌─────────────────────────┐
│  Web Interface (Flask)  │
│  Port: 5000             │
│  - Training orchestration│
│  - TensorFlow GPU       │
│  - Real-time updates    │
└───────────┬─────────────┘
            │
            │ HTTP API
            ▼
┌─────────────────────────┐
│ Feature Generator       │
│ Port: 5001              │
│ - PyTorch + torchcodec  │
│ - Spectrogram generation│
└─────────────────────────┘
```

## 🎛️ Training Configuration

### Presets

- **Quick** (1000 samples): ~5-10 minutes, good for testing
- **Standard** (2000 samples): ~15-20 minutes, recommended
- **High Quality** (4000 samples): ~30-40 minutes, best accuracy

### Advanced Settings

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| Number of Samples | Training samples to generate | 2000 | 500-10000 |
| Epochs | Training iterations | 30 | 10-100 |
| Batch Size | Samples per training batch | 512 | 128-2048 |
| Learning Rate | Model learning speed | 0.001 | 0.0001-0.01 |
| Probability Cutoff | Detection threshold | 0.97 | 0.80-0.99 |
| Sliding Window | Stability window size | 5 | 3-10 |

## 📦 Project Structure

```
wake-word-trainer/
├── app/
│   └── main.py                      # Flask app & training logic
├── templates/
│   └── index.html                   # Web interface
├── static/
│   ├── css/style.css               # Styles
│   └── js/app.js                   # Frontend logic
├── models/                          # Trained models output
├── training_jobs/                   # Training job data
├── Dockerfile                       # Main trainer container
├── Dockerfile.feature-generator    # Feature generation container
├── feature_generator_service.py    # Feature extraction service
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
└── README.md
```

## 📱 Using with ESPHome

After training completes:

1. Click "Download Model" to get the `.tflite` file
2. Add to your ESPHome configuration:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/your_wake_word.tflite
```

3. Upload to your ESP32-S3 device

For more details, see [ESPHome Micro Wake Word documentation](https://esphome.io/components/micro_wake_word/).

## 🐛 Troubleshooting

### GPU Not Detected

```bash
# Check GPU visibility in container
docker-compose exec wake-word-trainer nvidia-smi
```

If GPU isn't visible:
- Verify nvidia-docker2 is installed: `nvidia-docker version`
- Check Docker daemon includes nvidia runtime
- Restart Docker service

### Training Fails Immediately

Check logs:
```bash
docker-compose logs -f wake-word-trainer
docker-compose logs -f feature-generator
```

Common issues:
- Out of memory: Reduce batch size in advanced settings
- CUDA errors: Ensure CUDA 12.0 compatible GPU drivers

### Feature Generator Connection Error

```bash
# Verify feature-generator is running
docker-compose ps

# Check network connectivity
docker-compose exec wake-word-trainer curl -f http://feature-generator:5001/health
```

### Port Already in Use

Edit `docker-compose.yml`:

```yaml
services:
  wake-word-trainer:
    ports:
      - "8000:5000"  # Change external port
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project uses the following open-source libraries:
- [microWakeWord](https://github.com/kahrendt/microWakeWord) (Apache-2.0)
- [piper-sample-generator](https://github.com/rhasspy/piper-sample-generator) (MIT)
- [Flask](https://github.com/pallets/flask) (BSD-3-Clause)
- [TensorFlow](https://github.com/tensorflow/tensorflow) (Apache-2.0)
- [PyTorch](https://github.com/pytorch/pytorch) (BSD-3-Clause)

## 🙏 Acknowledgments

- [microWakeWord](https://github.com/kahrendt/microWakeWord) by Kevin Ahrendt for the training framework
- [Piper](https://github.com/rhasspy/piper) by Rhasspy for TTS sample generation
- [Home Assistant](https://www.home-assistant.io/) and [ESPHome](https://esphome.io/) communities

## 📚 Support

- 🐛 [Report Issues](https://github.com/chrisuthe/wake-word-trainer/issues)
- 💬 [Discussions](https://github.com/chrisuthe/wake-word-trainer/discussions)
- 📖 [Home Assistant Voice Documentation](https://www.home-assistant.io/voice_control/)

---

**Built with ❤️ for the Home Assistant community**
