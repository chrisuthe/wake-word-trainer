#!/usr/bin/env python3
"""
Feature Generator Service
Handles spectrogram generation using PyTorch/torchcodec
Runs separately from TensorFlow training to avoid CUDA conflicts
"""

from flask import Flask, request, jsonify
import os
import sys
from pathlib import Path

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/generate-features', methods=['POST'])
def generate_features():
    """
    Generate spectrograms from audio samples

    Expected JSON:
    {
        "samples_dir": "/path/to/samples",
        "output_dir": "/path/to/output"
    }
    """
    try:
        data = request.get_json()
        samples_dir = data.get('samples_dir')
        output_dir = data.get('output_dir')

        if not samples_dir or not output_dir:
            return jsonify({"error": "samples_dir and output_dir required"}), 400

        # Import here to avoid loading at startup
        from mmap_ninja.ragged import RaggedMmap
        from microwakeword.audio.clips import Clips
        from microwakeword.audio.spectrograms import SpectrogramGeneration

        print(f"Generating features from {samples_dir} to {output_dir}", flush=True)

        # Setup clips
        clips = Clips(
            input_directory=samples_dir,
            file_pattern='*.wav',
            max_clip_duration_s=None,
            remove_silence=False,
            random_split_seed=10,
            split_count=0.1,
        )

        # Generate features for each split
        os.makedirs(output_dir, exist_ok=True)

        splits = ["training", "validation", "testing"]
        for split in splits:
            print(f"Processing {split} split...", flush=True)
            out_dir = os.path.join(output_dir, split)
            os.makedirs(out_dir, exist_ok=True)

            split_name = "train"
            repetition = 1

            spectrograms = SpectrogramGeneration(
                clips=clips,
                augmenter=None,
                slide_frames=10 if split != "testing" else 1,
                step_ms=10,
            )

            if split == "validation":
                split_name = "validation"
            elif split == "testing":
                split_name = "test"

            RaggedMmap.from_generator(
                out_dir=os.path.join(out_dir, 'wakeword_mmap'),
                sample_generator=spectrograms.spectrogram_generator(split=split_name, repeat=repetition),
                batch_size=50,
                verbose=True,
            )
            print(f"{split} complete!", flush=True)

        print("Feature generation complete!", flush=True)

        return jsonify({
            "status": "success",
            "output_dir": output_dir,
            "splits": splits
        }), 200

    except Exception as e:
        print(f"Feature generation error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
