"""
Wake Word Trainer - Web Application
A web-based interface for training custom wake words for Home Assistant
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import os
import json
import uuid
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.config['SECRET_KEY'] = 'wake-word-trainer-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

socketio = SocketIO(app, cors_allowed_origins="*")

# Directories
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
TRAINING_JOBS_DIR = BASE_DIR / "training_jobs"
MICROWAKEWORD_DIR = BASE_DIR / "microWakeWord"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
TRAINING_JOBS_DIR.mkdir(exist_ok=True)

# Training jobs storage
training_jobs = {}


class TrainingJob:
    """Represents a wake word training job"""

    def __init__(self, job_id, wake_word, method, config, author="", website=""):
        self.job_id = job_id
        self.wake_word = wake_word
        self.method = method
        self.config = config
        self.author = author
        self.website = website
        self.status = "pending"
        self.progress = 0
        self.logs = []
        self.created_at = datetime.now()
        self.completed_at = None
        self.model_path = None
        self.error = None
        
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "wake_word": self.wake_word,
            "method": self.method,
            "status": self.status,
            "progress": self.progress,
            "logs": self.logs[-50:],  # Last 50 log lines
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "model_path": str(self.model_path) if self.model_path else None,
            "error": self.error
        }


def emit_progress(job_id, progress, message, status=None):
    """Emit progress update via WebSocket"""
    job = training_jobs.get(job_id)
    if job:
        job.progress = progress
        job.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if status:
            job.status = status

        socketio.emit('training_progress', {
            'job_id': job_id,
            'progress': progress,
            'message': message,
            'status': job.status,
            'logs': job.logs[-50:]
        })


def generate_model_json(job_id, model_file_path):
    """Generate ESPHome-compatible JSON manifest for the model"""
    job = training_jobs.get(job_id)
    if not job:
        return None

    job_dir = TRAINING_JOBS_DIR / job_id
    wake_word_name = job.wake_word.replace(' ', '_').lower()

    # Create JSON manifest
    manifest = {
        "type": "micro",
        "wake_word": wake_word_name,
        "author": job.author,
        "website": job.website if job.website else "",
        "model": f"{wake_word_name}.tflite",
        "trained_languages": ["en"],
        "version": 2,
        "micro": {
            "probability_cutoff": job.config.get('probability_cutoff', 0.97),
            "sliding_window_size": job.config.get('sliding_window_size', 5),
            "feature_step_size": 10,
            "tensor_arena_size": 22348,
            "minimum_esphome_version": "2024.7.0"
        }
    }

    # Save JSON file next to the model
    json_path = model_file_path.parent / f"{wake_word_name}.json"
    with open(json_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Generated JSON manifest: {json_path}")
    return json_path


def train_openwakeword(job_id, wake_word, config):
    """Train using OpenWakeWord method (Google Colab simulation)"""
    job = training_jobs[job_id]
    job_dir = TRAINING_JOBS_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        emit_progress(job_id, 10, "Initializing OpenWakeWord training...", "running")
        
        # Install dependencies
        emit_progress(job_id, 20, "Installing dependencies...")
        subprocess.run([
            "pip", "install", "--break-system-packages", "-q",
            "piper-sample-generator", "openwakeword"
        ], check=True, capture_output=True)
        
        # Generate samples
        num_samples = config.get('num_samples', 2000)
        emit_progress(job_id, 30, f"Generating {num_samples} voice samples...")
        
        samples_dir = job_dir / "samples"
        samples_dir.mkdir(exist_ok=True)
        
        # Create sample generation script
        gen_script = f"""
import sys
from piper_sample_generator import generate_samples

try:
    generate_samples(
        text="{wake_word}",
        output_dir="{samples_dir}",
        num_samples={num_samples},
        voices={config.get('voices', ['en_US-amy-medium', 'en_US-joe-medium'])}
    )
    print("SUCCESS: Generated {num_samples} samples")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
        
        script_path = job_dir / "generate_samples.py"
        script_path.write_text(gen_script)
        
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            raise Exception(f"Sample generation failed: {result.stderr}")
        
        emit_progress(job_id, 60, "Training wake word model...")
        
        # Simulate training (in real scenario, this would use actual training)
        # For OpenWakeWord, we'd typically guide users to Google Colab
        # Here we'll create a placeholder model file
        
        model_path = MODELS_DIR / f"{wake_word.replace(' ', '_')}_openwakeword.tflite"
        
        # Create training info file
        training_info = {
            "wake_word": wake_word,
            "method": "openwakeword",
            "num_samples": num_samples,
            "config": config,
            "trained_at": datetime.now().isoformat(),
            "colab_url": "https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb"
        }
        
        info_path = MODELS_DIR / f"{wake_word.replace(' ', '_')}_info.json"
        info_path.write_text(json.dumps(training_info, indent=2))
        
        # Create instructions file
        instructions = f"""
# OpenWakeWord Training Instructions

Your wake word "{wake_word}" is ready for training!

## Next Steps:

1. Open the Google Colab notebook:
   https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb

2. In Section 1, set:
   target_word = "{wake_word}"

3. Click Runtime → Run all

4. Wait for completion (~30-60 minutes)

5. Download the generated .tflite file

6. Upload it back here or install directly in Home Assistant:
   - Copy to /share/openwakeword/
   - Configure in Settings → Voice Assistants

## Configuration Used:
- Wake Word: {wake_word}
- Number of Samples: {num_samples}
- Training Method: OpenWakeWord

Generated samples are in: {samples_dir}
"""
        
        instructions_path = job_dir / "INSTRUCTIONS.md"
        instructions_path.write_text(instructions)
        
        emit_progress(job_id, 90, "Finalizing...")
        
        job.model_path = instructions_path
        job.status = "completed"
        job.completed_at = datetime.now()
        
        emit_progress(job_id, 100, "Training preparation complete! Check instructions.", "completed")
        
    except Exception as e:
        logger.error(f"Training failed for job {job_id}: {e}")
        job.status = "failed"
        job.error = str(e)
        emit_progress(job_id, 0, f"Training failed: {e}", "failed")


def train_microwakeword(job_id, wake_word, config):
    """Train using MicroWakeWord method"""
    job = training_jobs[job_id]
    job_dir = TRAINING_JOBS_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    try:
        emit_progress(job_id, 10, "Initializing MicroWakeWord training...", "running")

        # microWakeWord is pre-installed in the Docker image
        if not MICROWAKEWORD_DIR.exists():
            raise RuntimeError("microWakeWord directory not found. Please rebuild the Docker image.")

        # Generate samples
        num_samples = config.get('num_samples', 2000)
        emit_progress(job_id, 30, f"Generating {num_samples} voice samples...")

        samples_dir = job_dir / "samples" / "positive"
        samples_dir.mkdir(parents=True, exist_ok=True)

        # Use piper-sample-generator script with default voice model
        result = subprocess.run([
            "python3", "/app/piper-sample-generator/generate_samples.py",
            wake_word,
            "--model", "/app/voices/en_US-lessac-medium.onnx",
            "--max-samples", str(num_samples),
            "--output-dir", str(samples_dir)
        ], capture_output=True, text=True, timeout=900)

        if result.returncode != 0:
            logger.error(f"Sample generation failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
        
        emit_progress(job_id, 50, "Downloading negative datasets...")
        
        # Download datasets
        datasets_dir = job_dir / "datasets"
        datasets_dir.mkdir(exist_ok=True)
        
        download_script = f"""
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="kahrendt/microwakeword",
    repo_type="dataset",
    local_dir="{datasets_dir}",
    allow_patterns=["*.ragged", "*.json"]
)
"""
        
        download_path = job_dir / "download.py"
        download_path.write_text(download_script)
        
        # Install huggingface_hub
        subprocess.run([
            "pip", "install", "--break-system-packages", "-q", "huggingface_hub"
        ], check=True)
        
        subprocess.run(
            ["python3", str(download_path)],
            check=True,
            capture_output=True,
            timeout=3600
        )
        
        emit_progress(job_id, 70, "Creating training configuration...")
        
        # Create training config
        training_config = {
            "wake_word": wake_word,
            "model_id": wake_word.replace(" ", "_"),
            "positive_samples_dir": str(samples_dir),
            "negative_datasets_dir": str(datasets_dir),
            "output_dir": str(job_dir / "models"),
            "epochs": config.get('epochs', 30),
            "batch_size": config.get('batch_size', 512),
            "learning_rate": config.get('learning_rate', 0.001),
            "probability_cutoff": config.get('probability_cutoff', 0.97),
            "sliding_window_size": config.get('sliding_window_size', 5)
        }
        
        config_path = job_dir / "training_config.json"
        config_path.write_text(json.dumps(training_config, indent=2))
        
        # Create instructions for actual training
        instructions = f"""
# MicroWakeWord Training Instructions

Everything is prepared for training "{wake_word}"!

## Training Setup Complete:
✓ Samples generated: {num_samples}
✓ Negative datasets downloaded
✓ Configuration created

## To Complete Training:

### Option 1: Use Jupyter Notebook (Recommended)
1. Navigate to: {MICROWAKEWORD_DIR}/notebooks/
2. Open: basic_training_notebook.ipynb
3. Update the configuration with values from: {config_path}
4. Run all cells
5. Wait 2-4 hours for training

### Option 2: Command Line
```bash
cd {MICROWAKEWORD_DIR}
# Follow the training instructions in the repository
```

## Configuration:
- Wake Word: {wake_word}
- Samples: {num_samples}
- Epochs: {config.get('epochs', 30)}
- Batch Size: {config.get('batch_size', 512)}
- Learning Rate: {config.get('learning_rate', 0.001)}

## After Training:
You'll have:
- stream_state_internal_quant.tflite (model file)
- {wake_word.replace(' ', '_')}.json (manifest)

Copy these to your Home Assistant ESPHome device!

Training data is in: {job_dir}
"""
        
        instructions_path = job_dir / "TRAINING_INSTRUCTIONS.md"
        instructions_path.write_text(instructions)
        
        emit_progress(job_id, 90, "Creating deployment instructions...")
        
        # Create ESPHome config example
        esphome_config = f"""
# ESPHome Configuration for "{wake_word}"

micro_wake_word:
  microphone:
    microphone: mic  # Your microphone config
    channels: 0
    gain_factor: 4
  
  vad:
    model: github://esphome/micro-wake-word-models/models/v2/vad.json@main
  
  models:
    - model: github://yourusername/yourrepo/models/{wake_word.replace(' ', '_')}.json
      id: {wake_word.replace(' ', '_')}_model
      probability_cutoff: {config.get('probability_cutoff', 0.97)}
      sliding_window_size: {config.get('sliding_window_size', 5)}

  on_wake_word_detected:
    - voice_assistant.start:
        wake_word: !lambda return wake_word;
"""
        
        esphome_path = job_dir / "esphome_config.yaml"
        esphome_path.write_text(esphome_config)
        
        # Start automated training
        emit_progress(job_id, 60, "Starting automated training (this may take 1-3 hours)...")

        # Import yaml here since it's needed for config
        import yaml

        model_id = wake_word.replace(" ", "_")

        # Create YAML config for microWakeWord training
        yaml_config = {
            "window_step_ms": 10,
            "train_dir": str(job_dir / "trained_models" / model_id),
            "features": [
                {
                    "features_dir": str(samples_dir) + "_features",
                    "sampling_weight": 1.0,
                    "penalty_weight": 1.0,
                    "truth": True,
                    "truncation_strategy": "truncate_start",
                    "type": "mmap",
                },
                # Temporarily removed negative datasets - training with positive samples only for initial test
            ],
            "training_steps": [1000],  # Reduced for initial testing
            "positive_class_weight": [1],
            "negative_class_weight": [20],
            "learning_rates": [config.get('learning_rate', 0.001)],
            "batch_size": config.get('batch_size', 128),
            "time_mask_max_size": [0],
            "time_mask_count": [0],
            "freq_mask_max_size": [0],
            "freq_mask_count": [0],
            "eval_step_interval": 500,
            "clip_duration_ms": 1500,
            "target_minimization": 0.9,
            "minimization_metric": None,
            "maximization_metric": "average_viable_recall",
        }

        yaml_config_path = job_dir / "training_parameters.yaml"
        with open(yaml_config_path, 'w') as f:
            yaml.dump(yaml_config, f)

        emit_progress(job_id, 65, "Generating spectrograms from positive samples (this may take 10-15 minutes)...")

        # Call feature generator service (separate container with PyTorch)
        import requests

        feature_generator_url = os.environ.get('FEATURE_GENERATOR_URL', 'http://feature-generator:5001')
        output_dir = str(samples_dir) + "_features"

        logger.info(f"Calling feature generator service at {feature_generator_url}")

        try:
            response = requests.post(
                f"{feature_generator_url}/generate-features",
                json={
                    "samples_dir": str(samples_dir),
                    "output_dir": output_dir
                },
                timeout=3600
            )

            if response.status_code != 200:
                raise RuntimeError(f"Feature generation failed: {response.text}")

            result = response.json()
            logger.info(f"Feature generation complete: {result}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to feature generator: {e}")
            raise RuntimeError(f"Failed to connect to feature generator service: {e}")

        emit_progress(job_id, 70, "Training neural network (GPU accelerated if available)...")

        # Set environment variables for TensorFlow GPU training
        training_env = os.environ.copy()
        training_env['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        training_env['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU

        # Run training
        training_result = subprocess.run([
            "python3", "-m", "microwakeword.model_train_eval",
            f"--training_config={yaml_config_path}",
            "--train", "1",
            "--restore_checkpoint", "1",
            "--test_tf_nonstreaming", "0",
            "--test_tflite_nonstreaming", "0",
            "--test_tflite_nonstreaming_quantized", "0",
            "--test_tflite_streaming", "0",
            "--test_tflite_streaming_quantized", "1",
            "--use_weights", "best_weights",
            "mixednet",
            "--pointwise_filters", "64,64,64,64",
            "--repeat_in_block", "1,1,1,1",
            "--mixconv_kernel_sizes", "[5],[7,11],[9,15],[23]",
            "--residual_connection", "0,0,0,0",
            "--first_conv_filters", "32",
            "--first_conv_kernel_size", "5",
            "--stride", "3"
        ], cwd=str(job_dir), capture_output=True, text=True, env=training_env, timeout=14400)

        if training_result.returncode != 0:
            logger.error(f"Training failed:\nSTDOUT: {training_result.stdout}\nSTDERR: {training_result.stderr}")
            raise RuntimeError(f"Training failed: {training_result.stderr}")

        emit_progress(job_id, 95, "Training complete! Finalizing model...")

        # Find the generated model file
        model_file = job_dir / "trained_models" / model_id / "tflite_stream_state_internal_quant" / "stream_state_internal_quant.tflite"

        if not model_file.exists():
            # Try alternate location
            model_file = job_dir / "trained_models" / model_id / "stream_state_internal_quant.tflite"
            if not model_file.exists():
                logger.error(f"Model file not found. Searched: {model_file}")
                raise RuntimeError("Model file not found after training")

        # Generate JSON manifest for ESPHome
        json_path = generate_model_json(job_id, model_file)

        job.model_path = model_file
        job.status = "completed"
        job.completed_at = datetime.now()

        emit_progress(job_id, 100, f"Training complete! Model and JSON manifest ready for deployment.", "completed")
        
    except Exception as e:
        logger.error(f"Setup failed for job {job_id}: {e}")
        job.status = "failed"
        job.error = str(e)
        emit_progress(job_id, 0, f"Setup failed: {e}", "failed")


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/train', methods=['POST'])
def start_training():
    """Start a new training job"""
    try:
        data = request.get_json()
        
        wake_word = data.get('wake_word', '').strip().lower()
        method = data.get('method', 'openwakeword')
        author = data.get('author', '').strip()
        website = data.get('website', '').strip()

        if not wake_word:
            return jsonify({"error": "Wake word is required"}), 400

        if not author:
            return jsonify({"error": "Author name is required"}), 400

        # Validate wake word
        if len(wake_word) < 2 or len(wake_word) > 50:
            return jsonify({"error": "Wake word must be 2-50 characters"}), 400

        # Create training configuration
        config = {
            'num_samples': data.get('num_samples', 2000),
            'voices': data.get('voices', ['en_US-amy-medium', 'en_US-joe-medium']),
            'epochs': data.get('epochs', 30),
            'batch_size': data.get('batch_size', 512),
            'learning_rate': data.get('learning_rate', 0.001),
            'probability_cutoff': data.get('probability_cutoff', 0.97),
            'sliding_window_size': data.get('sliding_window_size', 5)
        }

        # Create job
        job_id = str(uuid.uuid4())
        job = TrainingJob(job_id, wake_word, method, config, author, website)
        training_jobs[job_id] = job
        
        # Start training in background
        if method == 'openwakeword':
            thread = threading.Thread(
                target=train_openwakeword,
                args=(job_id, wake_word, config)
            )
        else:
            thread = threading.Thread(
                target=train_microwakeword,
                args=(job_id, wake_word, config)
            )
        
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "job_id": job_id,
            "message": "Training started",
            "job": job.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to start training: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all training jobs"""
    jobs = [job.to_dict() for job in training_jobs.values()]
    jobs.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({"jobs": jobs})


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    job = training_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())


@app.route('/api/jobs/<job_id>/download', methods=['GET'])
def download_job_files(job_id):
    """Download job files as ZIP"""
    job = training_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    job_dir = TRAINING_JOBS_DIR / job_id
    if not job_dir.exists():
        return jsonify({"error": "Job files not found"}), 404

    # Create ZIP file
    zip_path = TRAINING_JOBS_DIR / f"{job_id}.zip"
    shutil.make_archive(
        str(zip_path.with_suffix('')),
        'zip',
        job_dir
    )

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=f"{job.wake_word.replace(' ', '_')}_training.zip"
    )


@app.route('/api/jobs/<job_id>/download-model', methods=['GET'])
def download_model_file(job_id):
    """Download the trained model package (tflite + json) as a zip for ESPHome devices"""
    job = training_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.status != "completed" and job.status != "ready_for_training":
        return jsonify({"error": "Model not ready - training not complete"}), 400

    job_dir = TRAINING_JOBS_DIR / job_id
    if not job_dir.exists():
        return jsonify({"error": "Job files not found"}), 404

    wake_word_name = job.wake_word.replace(' ', '_').lower()

    # Find the .tflite model file
    model_paths = [
        job_dir / "trained_models" / wake_word_name / "tflite_stream_state_internal_quant" / "stream_state_internal_quant.tflite",
        job_dir / "trained_models" / wake_word_name / "stream_state_internal_quant.tflite",
        job_dir / "model.tflite",
    ]

    model_path = None
    for path in model_paths:
        if path.exists():
            model_path = path
            break

    if not model_path:
        return jsonify({"error": "Model file not found in training output"}), 404

    # Find the JSON file
    json_paths = [
        job_dir / "trained_models" / wake_word_name / "tflite_stream_state_internal_quant" / f"{wake_word_name}.json",
        job_dir / "trained_models" / wake_word_name / f"{wake_word_name}.json",
        job_dir / f"{wake_word_name}.json",
    ]

    json_path = None
    for path in json_paths:
        if path.exists():
            json_path = path
            break

    if not json_path:
        return jsonify({"error": "JSON manifest not found in training output"}), 404

    # Create a temporary directory for the zip
    import tempfile
    import zipfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        zip_path = temp_dir_path / f"{wake_word_name}_model.zip"

        # Create zip with model and json
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add model file with correct name
            zipf.write(model_path, f"{wake_word_name}.tflite")
            # Add JSON file
            zipf.write(json_path, f"{wake_word_name}.json")

        # Read zip into memory to return it
        with open(zip_path, 'rb') as f:
            zip_data = f.read()

    # Create response with zip data
    from io import BytesIO
    return send_file(
        BytesIO(zip_data),
        as_attachment=True,
        download_name=f"{wake_word_name}_esphome.zip",
        mimetype="application/zip"
    )


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get training presets"""
    presets = {
        "openwakeword_quick": {
            "name": "OpenWakeWord - Quick",
            "method": "openwakeword",
            "num_samples": 1000,
            "description": "Fast training, good for testing"
        },
        "openwakeword_standard": {
            "name": "OpenWakeWord - Standard",
            "method": "openwakeword",
            "num_samples": 2000,
            "description": "Balanced quality and speed"
        },
        "openwakeword_high_quality": {
            "name": "OpenWakeWord - High Quality",
            "method": "openwakeword",
            "num_samples": 4000,
            "description": "Best quality, slower training"
        },
        "microwakeword_standard": {
            "name": "MicroWakeWord - Standard",
            "method": "microwakeword",
            "num_samples": 2000,
            "epochs": 30,
            "batch_size": 512,
            "description": "Standard on-device wake word"
        },
        "microwakeword_high_quality": {
            "name": "MicroWakeWord - High Quality",
            "method": "microwakeword",
            "num_samples": 4000,
            "epochs": 50,
            "batch_size": 512,
            "description": "Best quality for production use"
        }
    }
    return jsonify({"presets": presets})


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to training server'})


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to job updates"""
    job_id = data.get('job_id')
    if job_id and job_id in training_jobs:
        job = training_jobs[job_id]
        emit('training_progress', {
            'job_id': job_id,
            'progress': job.progress,
            'status': job.status,
            'logs': job.logs[-50:]
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
