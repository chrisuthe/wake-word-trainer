# 🚀 Getting Started with Wake Word Trainer

Welcome! This guide will help you get up and running with the Wake Word Trainer in minutes.

## What You'll Get

A modern web application that lets you:
- ✅ Train custom wake words like "Hey Betty" for Home Assistant
- ✅ Choose between easy (OpenWakeWord) or advanced (MicroWakeWord) training
- ✅ Monitor training progress in real-time
- ✅ Download and deploy models to your voice hardware
- ✅ Manage multiple wake word projects

## 📋 Prerequisites

Before you begin, make sure you have:

### Required
- **Docker** installed ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** installed (usually comes with Docker Desktop)
- **10GB free disk space** (for datasets and models)
- **4GB RAM minimum** (8GB recommended)

### Optional (for best experience)
- **GPU with CUDA** (for faster MicroWakeWord training)
- **Home Assistant** instance running
- **ESP32 voice hardware** (for deployment)

### Check Your System

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Check available disk space
df -h .

# Check available memory
free -h
```

## 🎯 Installation

### Method 1: Quick Start Script (Recommended)

The easiest way to get started:

```bash
# Navigate to the directory
cd wake-word-trainer

# Run the quick start script
./start.sh
```

The script will:
1. ✓ Check system requirements
2. ✓ Create necessary directories
3. ✓ Generate configuration files
4. ✓ Build the Docker container
5. ✓ Start the application

**That's it!** Open http://localhost:5000 in your browser.

### Method 2: Manual Setup

If you prefer to do it step by step:

```bash
# 1. Create directories
mkdir -p models training_jobs

# 2. Create environment file
cp .env.example .env

# 3. Build and start
docker-compose up -d

# 4. Check status
docker-compose ps
```

### Method 3: Docker Run (No Compose)

For simple deployments:

```bash
docker build -t wake-word-trainer .

docker run -d \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/training_jobs:/app/training_jobs \
  --name wake-word-trainer \
  wake-word-trainer
```

## 📱 Using the Web Interface

### 1. Access the Application

Open your browser and go to:
```
http://localhost:5000
```

You should see a modern dark-themed interface with the Wake Word Trainer dashboard.

### 2. Create Your First Wake Word

#### Step 1: Enter Your Wake Word
- Type your desired wake word (e.g., "hey betty")
- Keep it 2-4 syllables
- Use simple, distinct words

**Good examples:**
- ✓ hey betty
- ✓ okay assist
- ✓ computer start
- ✓ jarvis wake

**Avoid:**
- ✗ hey (too short)
- ✗ computer (too common in media)
- ✗ very long complicated phrases

#### Step 2: Choose Training Method

**OpenWakeWord (Recommended for Beginners)**
- ⚡ Easy to use
- ⏱️ 30-60 minutes training time
- 🌐 Training via Google Colab
- 💻 Works with any ESP32 hardware
- 🎯 Best for: Most users, quick testing

**MicroWakeWord (Advanced)**
- 🔬 Advanced configuration
- ⏱️ 2-4 hours training time
- 💪 Requires powerful PC or GPU
- 📟 Requires ESP32-S3 hardware
- 🎯 Best for: Maximum performance, lowest latency

#### Step 3: Select a Preset

Choose from pre-configured options:

**For OpenWakeWord:**
- **Quick** (1000 samples): Fast testing, ~15 minutes
- **Standard** (2000 samples): ⭐ Recommended, ~30 minutes
- **High Quality** (4000 samples): Best quality, ~60 minutes

**For MicroWakeWord:**
- **Standard**: Good balance
- **High Quality**: ⭐ Recommended for production

Or click **"Advanced Settings"** to customize:
- Number of samples
- Training epochs (MicroWakeWord)
- Batch size (MicroWakeWord)
- Learning rate (MicroWakeWord)
- Detection parameters

#### Step 4: Start Training

Click the **"🚀 Start Training"** button.

You'll see:
- Real-time progress bar
- Status updates (Initializing → Running → Completed)
- Training logs
- Estimated time remaining

### 3. Monitor Training Progress

The interface shows:
- **Progress Percentage** (0-100%)
- **Current Status** (color-coded badge)
- **Latest Message** (what's happening now)
- **Training Logs** (detailed activity)

**Status Colors:**
- 🟡 Yellow (Pending): Preparing
- 🔵 Blue (Running): Active training
- 🟢 Green (Completed): Success!
- 🔴 Red (Failed): Error occurred

### 4. Download Your Model

When training completes:
1. Click the **"📥 Download Files"** button
2. Extract the ZIP file
3. Follow the included instructions

**What you'll get:**
- Trained model file (`.tflite`)
- Configuration files
- ESPHome config examples
- Deployment instructions

## 🏠 Deploying to Home Assistant

### For OpenWakeWord Models

#### Step 1: Copy Model to Home Assistant
```bash
# Using Samba share
# Navigate to \\homeassistant\share\openwakeword\
# Copy your .tflite file there
```

#### Step 2: Configure Voice Assistant
1. Open Home Assistant
2. Go to **Settings** → **Voice Assistants**
3. Click **"Add Assistant"** or edit existing
4. Configure:
   - Name: "Hey Betty"
   - Language: English
   - Speech-to-text: Home Assistant Cloud (or Whisper)
   - Text-to-speech: Home Assistant Cloud (or Piper)
5. Click the **⋮** menu → **"Add streaming wake word"**
6. Select: **openWakeWord** → **Your model**
7. Save

#### Step 3: Configure Your Device
1. Go to **Settings** → **Devices & Services** → **ESPHome**
2. Select your device (e.g., ATOM Echo)
3. Enable **"Use wake word"**
4. Select your "Hey Betty" assistant
5. Test it: Say "Hey Betty, turn on the lights"

### For MicroWakeWord Models

#### Step 1: Host Your Model

**Option A: GitHub (Recommended)**
```bash
# 1. Create a repository on GitHub
# 2. Create a 'models' folder
# 3. Upload both files:
#    - hey_betty.json
#    - stream_state_internal_quant.tflite
# 4. Get the raw URL for the JSON file
```

**Option B: Local Hosting**
```bash
# Copy to Home Assistant
/config/custom_components/microwakeword/hey_betty.json
/config/custom_components/microwakeword/stream_state_internal_quant.tflite
```

#### Step 2: Update ESPHome Configuration

Add to your device's YAML:

```yaml
micro_wake_word:
  microphone:
    microphone: mic
    channels: 0
    gain_factor: 4
  
  vad:
    model: github://esphome/micro-wake-word-models/models/v2/vad.json@main
  
  models:
    - model: github://YOUR_USERNAME/YOUR_REPO/models/hey_betty.json
      id: hey_betty_model
      probability_cutoff: 0.97
      sliding_window_size: 5

  on_wake_word_detected:
    - voice_assistant.start:
        wake_word: !lambda return wake_word;
```

#### Step 3: Flash Your Device

```bash
# In ESPHome dashboard
# Click "Install" on your device
# Wait for compilation and upload
```

## 🧪 Testing Your Wake Word

### Initial Testing
1. Stand 2-3 meters from your device
2. Say your wake word clearly: **"Hey Betty"**
3. Watch for LED feedback (usually blue = listening)
4. Say a command: "Turn on the lights"

### Testing Different Scenarios
- ✅ Normal speaking volume
- ✅ From different distances (1-5 meters)
- ✅ Different voices (male, female, children)
- ✅ With background music
- ✅ With TV playing
- ✅ In different rooms

### Check Logs

**For OpenWakeWord:**
```
Settings → System → Logs
Look for: [openwakeword] Wake word detected
```

**For MicroWakeWord:**
```
Settings → Devices & Services → ESPHome → Your Device → Logs
Look for: [micro_wake_word] Wake word 'hey betty' detected!
```

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs -f

# Try restart
docker-compose restart

# Rebuild from scratch
docker-compose down
docker-compose up -d --build
```

### Can't Access Web Interface

```bash
# Verify container is running
docker-compose ps

# Check if port 5000 is available
netstat -an | grep 5000

# Try accessing via IP address
http://YOUR_SERVER_IP:5000

# Change port if 5000 is busy
# Edit docker-compose.yml:
ports:
  - "8000:5000"
```

### Training Fails

**Check logs in the web interface:**
1. Scroll down to "Training Logs" section
2. Look for error messages
3. Common issues:
   - **Out of disk space**: Clean old jobs, free up space
   - **Out of memory**: Close other apps, increase Docker memory limit
   - **Network issues**: Check internet connection for dataset downloads

**Solutions:**
```bash
# Free up disk space
docker system prune -a
rm -rf ./training_jobs/*

# Increase Docker memory (Docker Desktop)
# Settings → Resources → Memory (set to 8GB)

# Check Docker logs
docker-compose logs -f wake-word-trainer
```

### Wake Word Not Detecting

**For OpenWakeWord:**
1. Check the model is in `/share/openwakeword/`
2. Verify openWakeWord add-on is running
3. Check Wyoming integration is configured
4. Enable "Use wake word" on device
5. Try lowering probability cutoff (retrain)

**For MicroWakeWord:**
1. Verify model URL is correct in YAML
2. Check ESP32 logs for errors
3. Ensure ESP32-S3 hardware (not ESP32 or ESP32-S3)
4. Flash latest ESPHome version
5. Adjust `probability_cutoff` down (0.90-0.95)

### Too Many False Activations

**Solutions:**
1. Increase `probability_cutoff` (0.98 or 0.99)
2. Move device away from speakers
3. Use different wake word (less common)
4. Retrain with more samples
5. Enable Voice Activity Detection (VAD)

## 📚 Next Steps

### Improve Your Model
- Generate more samples (3000-5000)
- Try different pronunciations
- Train for more epochs (MicroWakeWord)
- Test and iterate

### Create Multiple Wake Words
- Train different wake words for different rooms
- Use different models for different family members
- Experiment with creative phrases

### Advanced Features
- Integrate with AI assistants (ChatGPT, Claude)
- Create custom responses
- Set up automation based on wake word
- Build multi-language support

## 💡 Tips for Success

1. **Start Simple**
   - Use OpenWakeWord first
   - Choose a clear, distinct wake word
   - Use preset configurations

2. **Test Thoroughly**
   - Try multiple distances
   - Test with background noise
   - Have different people test it

3. **Be Patient**
   - First models often need adjustment
   - Iterate and improve
   - Join the community for help

4. **Document What Works**
   - Note successful parameters
   - Track testing results
   - Share learnings with others

## 🤝 Getting Help

### Community Resources
- **Home Assistant Forum**: https://community.home-assistant.io/
- **ESPHome Discord**: https://discord.gg/KhAMKrd
- **Reddit**: r/homeassistant

### Documentation
- **This Application**: README.md
- **Home Assistant Voice**: https://www.home-assistant.io/voice_control/
- **OpenWakeWord**: https://github.com/dscripka/openWakeWord
- **MicroWakeWord**: https://github.com/kahrendt/microWakeWord

### Reporting Issues
- Check existing issues first
- Provide logs from the web interface
- Include Docker logs if relevant
- Describe what you expected vs. what happened

## 🎉 You're Ready!

You now have everything you need to:
- ✅ Train custom wake words
- ✅ Deploy to Home Assistant
- ✅ Test and iterate
- ✅ Troubleshoot issues

**Ready to begin?** Open http://localhost:5000 and create your first wake word!

---

**Questions?** Check the QUICK_REFERENCE.md for common commands and solutions.

**Enjoying this tool?** Star the repository and share with others! ⭐
