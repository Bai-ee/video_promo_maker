#!/bin/bash

# Run the image preview generator
node assets/dynamic-video-template/run_image.js

# If on macOS, open the preview image
if [[ "$OSTYPE" == "darwin"* ]]; then
    open scene.png
fi 