#!/bin/bash

# Enable error handling
set -e

# Log file
LOG_FILE="ffmpeg_render.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Clear previous log
> "$LOG_FILE"

log "Starting video render process"

# Check if audio file exists
AUDIO_FILE="assets/dynamic-video-template/temp_audio.mp3"
if [ -f "$AUDIO_FILE" ]; then
    log "Found audio file: $AUDIO_FILE"
    
    # Get audio duration
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE")
    DURATION=${DURATION%.*} # Remove decimal places
    log "Audio duration: $DURATION seconds"
    
    # Create video with audio
    log "Rendering video with audio..."
    ffmpeg -y -loop 1 -i scene.png \
           -i "$AUDIO_FILE" \
           -vf "scale=500:600,fps=30" \
           -c:v libx264 \
           -c:a aac \
           -shortest \
           -pix_fmt yuv420p \
           output.mp4 2>&1 | tee -a "$LOG_FILE"
else
    # No audio file found, create silent video with 30s duration
    log "No audio file found. Creating silent video with 30s duration"
    ffmpeg -y -loop 1 -i scene.png \
           -vf "scale=500:600,fps=30" \
           -c:v libx264 \
           -t 30 \
           -pix_fmt yuv420p \
           output.mp4 2>&1 | tee -a "$LOG_FILE"
fi

# Check if output video exists
if [ -f "output.mp4" ]; then
    # Get video details
    log "Video render complete. Details:"
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 output.mp4 2>/dev/null | \
        xargs -I {} echo "Duration: {}s" | tee -a "$LOG_FILE"
    ls -lh output.mp4 | awk '{print "Size: " $5}' | tee -a "$LOG_FILE"
    log "Output saved to: $(pwd)/output.mp4"
else
    log "Error: Failed to create output video"
    exit 1
fi
