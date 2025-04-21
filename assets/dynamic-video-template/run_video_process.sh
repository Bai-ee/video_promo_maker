#!/bin/bash

# Log file
LOG_FILE="process.log"

# Function to log messages
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Start logging
log "Starting video process"

# Run the render_scene.js script to update the template
ARTIST_NAME="AKILA"
log "Injecting artist info: $ARTIST_NAME"
log "Updating template file"
node assets/dynamic-video-template/render_scene.js

# Check if the template was updated correctly
if [ -f "updated_template.html" ] && grep -q "AKILA" updated_template.html; then
  log "Template updated successfully with artist $ARTIST_NAME"
else
  log "Template update failed"
  exit 1
fi

# Render the video
log "Rendering Video"
yes | ./ffmpeg_render.sh

# Check if the video was rendered successfully
if [ $? -eq 0 ]; then
  log "Video rendered successfully"
else
  log "Video rendering failed"
  exit 1
fi

log "Video process completed" 