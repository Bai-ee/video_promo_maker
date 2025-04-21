#!/bin/bash

# Create a video from the single rendered scene image
ffmpeg -loop 1 -i scene.png -vf "scale=500:600,fps=30" -c:v libx264 -t 5 -pix_fmt yuv420p output.mp4
