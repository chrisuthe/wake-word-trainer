# Wake Word Trainer - Quick Reference 🚀

## Quick Start (3 Commands)

```bash
cd wake-word-trainer
./start.sh
# Open http://localhost:5000
```

## Essential Commands

### Start/Stop
```bash
docker-compose up -d        # Start in background
docker-compose down         # Stop and remove
docker-compose restart      # Restart
docker-compose stop         # Stop (keep containers)
docker-compose start        # Start (existing containers)
```

### Logs & Monitoring
```bash
docker-compose logs -f                    # Follow all logs
docker-compose logs -f wake-word-trainer  # Follow specific service
docker-compose ps                         # List running containers
docker stats                              # Resource usage
```

### Maintenance
```bash
docker-compose up -d --build    # Rebuild and restart
docker-compose pull             # Update images
docker system prune -a          # Clean up Docker
```

## Web Interface

**URL**: http://localhost:5000

### Creating a Wake Word
1. Enter wake word (e.g., "hey betty")
2. Choose method:
   - **OpenWakeWord** (Easy): 30-60 min, any hardware
   - **MicroWakeWord** (Advanced): 2-4 hrs, ESP32-S3
3. Select preset or customize
4. Click "Start Training"

### Presets

**OpenWakeWord**
- Quick: 1000 samples (~15 min)
- Standard: 2000 samples (~30 min) ⭐
- High Quality: 4000 samples (~60 min)

**MicroWakeWord**
- Standard: 2000 samples, 30 epochs
- High Quality: 4000 samples, 50 epochs ⭐

## File Locations

```
wake-word-trainer/
├── models/            # Trained models (persist)
├── training_jobs/     # Training data (persist)
├── app/              # Application code
├── templates/        # HTML templates
└── static/           # CSS & JS
```

## Deployment to Home Assistant

### OpenWakeWord
1. Download `.tflite` file
2. Copy to HA: `/share/openwakeword/`
3. Settings → Voice Assistants
4. Select openWakeWord + your model

### MicroWakeWord
1. Download model package
2. Upload to GitHub or host locally
3. Add to ESPHome config:
```yaml
micro_wake_word:
  models:
    - model: github://user/repo/models/wake_word.json
```

## Troubleshooting

### App won't start
```bash
docker-compose logs -f
docker-compose restart
```

### Port 5000 in use
```bash
# Edit docker-compose.yml, change ports:
ports:
  - "8000:5000"  # Use port 8000 instead
```

### Out of disk space
```bash
docker system prune -a          # Clean Docker
rm -rf ./training_jobs/*        # Clean old jobs
```

### Training fails
- Check logs in web UI
- Ensure 10GB+ free space
- For MicroWakeWord: 8GB+ RAM needed

## Configuration

### Environment Variables (.env)
```bash
PORT=5000                  # Web interface port
FLASK_ENV=production      # production/development
MAX_SAMPLES=10000         # Maximum samples allowed
```

### Docker Resources
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

## API Endpoints

```http
POST /api/train              # Start training
GET /api/jobs                # List all jobs
GET /api/jobs/{id}           # Get job details
GET /api/jobs/{id}/download  # Download files
GET /api/presets             # Get presets
```

## Common Wake Words

✅ **Good Examples**
- "hey betty"
- "okay assist"
- "computer start"
- "jarvis hello"

❌ **Avoid**
- "hey" (too common)
- "okay" (too short)
- "computer" (used in media)
- Very long phrases

## Training Parameters

### Critical Settings
| Parameter | OpenWakeWord | MicroWakeWord |
|-----------|--------------|---------------|
| Samples | 2000-4000 | 2000-4000 |
| Epochs | N/A | 30-50 |
| Batch Size | N/A | 512 |
| Probability Cutoff | N/A | 0.95-0.98 |

### Tuning Tips
- **More samples** = Better quality, longer training
- **More epochs** = Better training, risk overfitting
- **Higher cutoff** = Fewer false activations
- **Larger window** = More stable, higher latency

## System Requirements

### Minimum
- 4GB RAM
- 10GB disk space
- Docker installed

### Recommended
- 8GB RAM
- 20GB disk space
- SSD storage
- GPU (for MicroWakeWord)

## Support & Resources

- **Documentation**: README.md
- **Home Assistant**: https://www.home-assistant.io/voice_control/
- **OpenWakeWord**: https://github.com/dscripka/openWakeWord
- **MicroWakeWord**: https://github.com/kahrendt/microWakeWord
- **Community**: https://community.home-assistant.io/

## Tips for Success

1. **Start with OpenWakeWord** - Much easier
2. **Use simple wake words** - 2-3 syllables
3. **Test thoroughly** - Different voices, distances
4. **Be patient** - First models may need adjustment
5. **Iterate** - Retrain with tweaks as needed

## Quick Fixes

### Cannot access web UI
```bash
# Check if running
docker ps

# Check logs
docker-compose logs -f

# Try restart
docker-compose restart

# Access via IP
http://YOUR_SERVER_IP:5000
```

### Training stuck
```bash
# Check progress
docker-compose logs -f

# Restart training
# (Cancel in UI and start new job)
```

### Need more disk space
```bash
# Check usage
du -sh models/ training_jobs/

# Clean old jobs
rm -rf training_jobs/*/

# Docker cleanup
docker system prune -a -f
```

---

## One-Line Commands

### Complete Setup
```bash
git clone <repo> && cd wake-word-trainer && ./start.sh
```

### Quick Restart
```bash
docker-compose down && docker-compose up -d --build
```

### View Live Logs
```bash
docker-compose logs -f | grep -i "training\|error\|complete"
```

### Backup Models
```bash
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/
```

---

**Ready to train?** Run `./start.sh` and open http://localhost:5000 🎙️
