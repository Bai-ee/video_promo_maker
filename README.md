# Underground Existence Video Generator

This tool generates promotional videos for artists using a template-based system with live watching capabilities.

## Setup

1. Make sure you have Node.js and FFmpeg installed on your system.
2. Install dependencies:
```bash
npm install
```

## Running Videos

To properly generate videos, follow these steps in order:

1. **Start the Template Watcher**
   First, start the template watcher in a separate terminal window:
   ```bash
   node watcher.js
   ```
   This will watch for changes in `base_template.html` and automatically sync them to `updated_template.html`.
   Keep this running while making template changes.

2. **Update Artist Information**
   - Artist data is stored in `assets/artists.json`
   - Artist images should be placed in `assets/artist_thumbnails/`
   - Background images go in `assets/backgrounds/`

3. **Modify the Template**
   - Edit `assets/dynamic-video-template/base_template.html` for template changes
   - The watcher will automatically sync changes to `updated_template.html`
   - Changes are applied in real-time

4. **Generate Video**
   In a new terminal window, run:
   ```bash
   node assets/dynamic-video-template/render_scene.js && assets/dynamic-video-template/ffmpeg_render.sh
   ```
   This will:
   - Update the template with the selected artist's information
   - Generate a screenshot of the rendered page
   - Convert the screenshot to a video using FFmpeg

## Template Structure

The template uses the following placeholders:
- Artist name (replaces "BAI-EE")
- Artist image (in the thumbnail div)
- Artist genre
- Mixes information (using <!-- MIXES_PLACEHOLDER -->)

## Troubleshooting

1. If the template isn't updating:
   - Ensure the watcher is running (`node watcher.js`)
   - Check for any error messages in the watcher terminal
   - Try restarting the watcher

2. If the video isn't generating:
   - Check that all paths in `render_scene.js` are correct
   - Verify that the artist index in `render_scene.js` is set to the desired artist
   - Ensure FFmpeg is properly installed

3. If images aren't displaying:
   - Verify image paths in `assets/artists.json`
   - Check that images exist in the correct directories
   - Ensure image filenames match the JSON configuration

## File Structure
```
assets/
├── dynamic-video-template/
│   ├── base_template.html    # Main template file (edit this for styles)
│   ├── updated_template.html # Auto-generated (don't edit)
│   ├── render_scene.js      # Template update script
│   └── ffmpeg_render.sh     # Video rendering script
└── artists.json             # Artist data
``` 