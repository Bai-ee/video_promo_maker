# Faceless Video Maker

A SaaS product for generating promotional videos for artists with dynamic content and audio processing.

## System Architecture

The system consists of several key components:

1. **Template System**
   - `base_template.html`: The master template file
   - `updated_template.html`: Working copy that gets modified during rendering
   - Template watcher (`watcher.js`) that monitors template changes
   - Dynamic placeholders for artist data:
     - `BAI-EE`: Artist name placeholder
     - `path/to/your/image.jpg`: Thumbnail placeholder
     - `GENRE_PLACEHOLDER`: Genre text placeholder
     - `<!-- MIXES_PLACEHOLDER -->`: Mix information placeholder

2. **Dynamic Data Management**
   - `assets/artists.json`: Main data source for all artists
   - Data structure per artist:
     ```json
     {
       "artistName": "ARTIST_NAME",
       "artistGenre": "GENRE | LOCATION",
       "artistImageFilename": "img/artists/artist.jpg",
       "mixes": [
         {
           "mixTitle": "Mix Title",
           "mixDuration": "120:00",
           "mixDateYear": "2024",
           "mixArweaveURL": "https://arweave.net/..."
         }
       ]
     }
     ```

3. **Template Watcher System**
   - Location: `watcher.js`
   - Purpose: Real-time template synchronization
   - Functionality:
     ```javascript
     // Start watcher
     node watcher.js
     
     // Output example:
     Watching for changes in base_template.html...
     File base_template.html has been changed. Copying contents to updated_template.html...
     Contents copied to updated_template.html successfully.
     ```
   - Monitors changes to `base_template.html`
   - Automatically updates `updated_template.html`
   - Keeps running while making template changes
   - No need to restart for template updates

4. **Rendering Engine**
   - `render_scene.js`: Main rendering script
   - Puppeteer for HTML to PNG conversion
   - FFmpeg for video generation

5. **Audio Processing**
   - `audio-processor.ts`: Handles downloading and processing mix audio
   - Creates 30-second clips with fade in/out

6. **Asset Management**
   - Artist thumbnails in `assets/artist_thumbnails/`
   - Background images in `assets/backgrounds/`
   - Logos in `assets/logos/`
   - Font files in `assets/font/`

## Working with Templates and Dynamic Data

### Template Modifications
1. Start the template watcher in a dedicated terminal:
   ```bash
   node watcher.js
   ```
   Keep this running while making template changes.

2. Edit `base_template.html`:
   - Modify HTML/CSS as needed
   - Use predefined placeholders:
     ```html
     <h1>BAI-EE</h1>  <!-- Artist name placeholder -->
     <h2>GENRE_PLACEHOLDER</h2>  <!-- Genre placeholder -->
     <div class="mixes">
       <!-- MIXES_PLACEHOLDER -->  <!-- Mix info placeholder -->
     </div>
     ```
   - Changes are automatically synced to `updated_template.html`

### Dynamic Data Setup
1. Update artist information in `assets/artists.json`:
   ```json
   {
     "artists": [
       {
         "artistName": "ARTIST_NAME",
         "artistGenre": "GENRE | LOCATION",
         "artistImageFilename": "img/artists/artist.jpg",
         "mixes": [...]
       }
     ]
   }
   ```

2. Add required assets:
   - Place artist image in `assets/artist_thumbnails/`
   - Ensure image filename matches `artistImageFilename`
   - Verify mix URLs are accessible

3. Test data integration:
   ```bash
   # Generate a test video with random artist
   node assets/dynamic-video-template/render_scene.js && yes | assets/dynamic-video-template/ffmpeg_render.sh
   ```

## Workflow for Making Changes

### Style Updates
1. Modify CSS within `base_template.html`
2. Test with different artists to ensure responsive design
3. Key style sections:
   - Main container (.content-wrapper)
   - Thumbnail (.top-thumbnail)
   - Artist info (.artist-info)
   - Mix details (.mixes)
   - Footer (.footer)

### Asset Updates
1. Artist thumbnails: Add to `assets/artist_thumbnails/`
2. Background images: Add to `assets/backgrounds/`
3. Logos: Add to `assets/logos/`
4. Update file references in `render_scene.js`

## Generating Videos

### Prerequisites
1. Ensure all dependencies are installed:
   ```bash
   npm install
   ```
2. Compile TypeScript files:
   ```bash
   npm run build
   ```

### Steps to Generate a Video

1. **Start Template Watcher** (if making template changes)
   ```bash
   node watcher.js
   ```

2. **Generate Video**
   ```bash
   node assets/dynamic-video-template/render_scene.js && yes | assets/dynamic-video-template/ffmpeg_render.sh
   ```
   This command:
   - Randomly selects an artist
   - Generates the HTML with artist info
   - Creates a screenshot
   - Processes audio from the mix
   - Renders final video with FFmpeg

3. **Output**
   - The final video is saved as `output.mp4`
   - Duration: ~32 seconds
   - Resolution: 500x600
   - Includes 30-second audio clip with fades

### Customizing Video Generation

To modify video parameters:

1. **Audio Duration**: Update in `audio-processor.ts`
   - Default clip duration: 30 seconds
   - Fade in/out: 2 seconds each

2. **Video Quality**: Adjust in `ffmpeg_render.sh`
   - Resolution: 500x600
   - Frame rate: 30fps
   - Codec: h264

3. **Template Layout**: Modify in `base_template.html`
   - Dimensions
   - Font sizes
   - Spacing
   - Colors

## Troubleshooting

1. **Audio Issues**
   - Check mix URL accessibility
   - Verify temp_audio.mp3 location
   - Check FFmpeg installation

2. **Visual Issues**
   - Verify asset paths
   - Check template watcher logs
   - Inspect generated HTML

3. **Rendering Issues**
   - Check Puppeteer installation
   - Verify FFmpeg configuration
   - Check disk space for temporary files

## Development Guidelines

1. **Adding Features**
   - Update TypeScript files in `lib/`
   - Rebuild using `npm run build`
   - Test with multiple artists

2. **Testing Changes**
   - Run multiple test renders
   - Check different artist configurations
   - Verify audio processing
   - Validate template responsiveness

3. **Best Practices**
   - Keep template changes in `base_template.html`
   - Use absolute paths in `render_scene.js`
   - Clean up temporary files
   - Handle errors gracefully

## Template Structure

The template uses the following placeholders:
- Artist name (replaces "BAI-EE")
- Artist image (in the thumbnail div)
- Artist genre
- Mixes information (using <!-- MIXES_PLACEHOLDER -->)

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