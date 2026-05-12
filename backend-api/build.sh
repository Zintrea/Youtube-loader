#!/bin/bash
# Build script for Render - installs FFmpeg and Python deps
set -e

# Install FFmpeg (required by yt-dlp for merging video+audio)
apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
pip install -r Requirements.txt

echo "Build complete"
