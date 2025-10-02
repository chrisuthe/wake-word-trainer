# 🎙️ Wake Word Trainer - Complete Web Application Package

## 📦 What's Included

This is a **complete, production-ready web application** for training custom wake words for Home Assistant. Everything you need is in this package!

## 🎯 Features

✅ **Modern Web Interface** - Clean, dark-themed UI
✅ **Two Training Methods** - OpenWakeWord (easy) & MicroWakeWord (advanced)  
✅ **Real-time Progress** - Live updates via WebSocket
✅ **Configurable Parameters** - Full control over training settings
✅ **Training History** - Track all your projects
✅ **Easy Deployment** - Docker containerized, one-command start
✅ **Comprehensive Docs** - Multiple guides included

## 📁 Package Contents

```
wake-word-trainer-webapp.zip
│
└── wake-word-trainer/
    ├── 📄 README.md                    # Complete documentation
    ├── 📄 GETTING_STARTED.md           # Beginner-friendly guide
    ├── 📄 QUICK_REFERENCE.md           # Commands cheat sheet
    │
    ├── 🚀 start.sh                     # One-click startup script
    ├── 🐳 Dockerfile                   # Docker configuration
    ├── 🐳 docker-compose.yml           # Docker Compose setup
    ├── ⚙️  .env.example                # Environment template
    ├── 📝 requirements.txt             # Python dependencies
    │
    ├── app/
    │   └── main.py                     # Flask application
    │
    ├── templates/
    │   └── index.html                  # Web interface
    │
    ├── static/
    │   ├── css/
    │   │   └── style.css              # Modern styling
    │   └── js/
    │       └── app.js                  # Frontend logic
    │
    ├── models/                         # (Created on first run)
    └── training_jobs/                  # (Created on first run)
```

## ⚡ Quick Start (3 Commands)

```bash
# 1. Extract the ZIP
unzip wake-word-trainer-webapp.zip
cd wake-word-trainer

# 2. Start the application
./start.sh

# 3. Open in browser
# http://localhost:5000
```

That's it! You're ready to train wake words!

## 📖 Documentation Guide

### Start Here 👈
1. **GETTING_STARTED.md** - Complete beginner's guide
   - Installation instructions
   - Using the web interface
   - Deploying to Home Assistant
   - Troubleshooting

### For Quick Reference 📋
2. **QUICK_REFERENCE.md** - Commands and solutions
   - Essential Docker commands
   - Common tasks
   - Quick fixes
   - API reference

### For Deep Dive 📚
3. **README.md** - Complete technical documentation
   - Architecture details
   - Configuration options
   - API documentation
   - Security considerations

## 🎯 What Can You Do?

### Create Custom Wake Words
- "Hey Betty" for your personal assistant
- "Okay House" for home control
- "Computer Start" for sci-fi vibes
- Any phrase you can imagine!

### Two Training Methods

**OpenWakeWord (Recommended)**
- ✅ Easy to use, no technical knowledge needed
- ✅ 30-60 minutes training time
- ✅ Works with any ESP32 hardware
- ✅ Training happens in Google Colab (cloud)

**MicroWakeWord (Advanced)**
- ✅ On-device detection for ESP32-S3
- ✅ Lowest possible latency (~75ms)
- ✅ Maximum privacy (all local)
- ⚠️ Requires powerful PC/GPU
- ⚠️ 2-4 hours training time

### Full Configuration Control
- Number of voice samples (500-10,000)
- Training epochs and batch size
- Detection sensitivity
- And much more!

## 🖥️ System Requirements

### Minimum
- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: Version 20.10+
- **RAM**: 4GB
- **Disk**: 10GB free space
- **CPU**: Multi-core recommended

### Recommended
- **RAM**: 8GB
- **Disk**: 20GB SSD
- **CPU**: 4+ cores
- **GPU**: NVIDIA with CUDA (for MicroWakeWord)

## 🚀 Deployment Options

### Development (Local Testing)
```bash
python app/main.py
# Access at http://localhost:5000
```

### Production (Docker)
```bash
docker-compose up -d
# Runs as daemon, auto-restarts
```

### Production (Docker with GPU)
```bash
# Uncomment GPU section in docker-compose.yml
docker-compose up -d
# Enables NVIDIA GPU for faster training
```

## 🎨 Web Interface Features

### Dashboard
- Clean, modern design
- Dark theme (easy on eyes)
- Responsive (works on mobile)
- Intuitive navigation

### Training Form
- Wake word input with validation
- Method selection (visual cards)
- Preset configurations
- Advanced settings (expandable)
- Real-time validation

### Progress Monitoring
- Animated progress bar
- Live status updates
- Training logs (scrollable)
- Download button when complete

### Training History
- All past jobs
- Status tracking
- Quick re-download
- Job management

## 🔧 Configuration Examples

### Basic Setup (Default)
```bash
PORT=5000
FLASK_ENV=production
```

### Custom Port
```bash
PORT=8080  # Use port 8080 instead
```

### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

### GPU Support
```yaml
# In docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## 📊 Training Workflow

```
1. Enter Wake Word
   ↓
2. Choose Method
   ↓
3. Configure Parameters
   ↓
4. Start Training
   ↓
5. Monitor Progress (Real-time)
   ↓
6. Download Model
   ↓
7. Deploy to Home Assistant
   ↓
8. Test & Iterate
```

## 🎓 Learning Path

### Beginner
1. Read GETTING_STARTED.md
2. Use OpenWakeWord method
3. Use Standard preset
4. Train "hey betty"
5. Deploy and test

### Intermediate
1. Try custom parameters
2. Test different wake words
3. Compare presets
4. Monitor training metrics

### Advanced
1. Use MicroWakeWord method
2. Fine-tune parameters
3. Enable GPU training
4. Optimize for production
5. Contribute improvements

## 🔐 Security Notes

### Default Setup (Safe for Local)
- Binds to 0.0.0.0:5000
- No authentication
- Safe for home networks

### Production Setup (Recommended)
- Add reverse proxy (nginx, Traefik)
- Enable HTTPS
- Add authentication
- Set resource limits
- Use secrets management

### Data Privacy
- All training data stays local
- No data sent to cloud (except OpenWakeWord training via Colab)
- Models stored locally
- Full control over your data

## 🤝 Community & Support

### Getting Help
1. Check GETTING_STARTED.md troubleshooting section
2. Search Home Assistant community forum
3. Ask on ESPHome Discord
4. Open GitHub issue (if applicable)

### Contributing
- Report bugs
- Suggest features
- Improve documentation
- Share trained models
- Help other users

### Resources
- **Home Assistant**: https://www.home-assistant.io/voice_control/
- **OpenWakeWord**: https://github.com/dscripka/openWakeWord
- **MicroWakeWord**: https://github.com/kahrendt/microWakeWord
- **ESPHome**: https://esphome.io/components/micro_wake_word/

## ✨ What's Next?

After setup, you can:
1. ✅ Train your first wake word
2. ✅ Deploy to Home Assistant
3. ✅ Test with your voice hardware
4. ✅ Create multiple wake words
5. ✅ Share with the community

## 🎯 Use Cases

### Home Automation
- "Hey Betty, turn on the lights"
- "Okay House, lock the doors"
- "Computer, start movie mode"

### Personal Assistant
- "Hey Assistant, what's the weather?"
- "Okay Helper, set a timer"
- "Computer, add milk to shopping list"

### Family Members
- "Hey Mom" for parent's assistant
- "Okay Kids" for children's rooms
- "Computer Dad" for office

### Room-Specific
- "Kitchen Start" for kitchen commands
- "Bedroom Help" for bedroom control
- "Office Computer" for work tasks

## 📝 Version Information

- **Application**: 1.0.0
- **Python**: 3.11+
- **Flask**: 3.0.0
- **Docker**: Recommended 20.10+

## 📜 License

- **This Application**: MIT License (or your choice)
- **OpenWakeWord**: MIT License
- **MicroWakeWord**: Apache 2.0 License
- **Home Assistant**: Apache 2.0 License

## 🙏 Credits

- **Application**: Wake Word Trainer Team
- **OpenWakeWord**: David Scripka
- **MicroWakeWord**: Kevin Ahrendt
- **Home Assistant**: Nabu Casa & Community
- **ESPHome**: ESPHome Team

## 🚦 Ready to Start?

```bash
cd wake-word-trainer
./start.sh
```

Then open: **http://localhost:5000**

---

## 📞 Need Help?

1. **Quick Questions**: See QUICK_REFERENCE.md
2. **Getting Started**: Read GETTING_STARTED.md
3. **Deep Dive**: Check README.md
4. **Still Stuck**: Ask the community!

---

**Happy wake word training!** 🎙️✨

Create voice assistants that truly understand YOUR voice and YOUR commands!
