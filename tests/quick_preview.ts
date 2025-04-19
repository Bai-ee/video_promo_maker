import { exec } from 'child_process';
import { promisify } from 'util';
import { generateImages } from '../lib/images';
import path from 'path';
import fs from 'fs';
import fetch from 'node-fetch';

const execAsync = promisify(exec);

// Video dimensions
const VIDEO_WIDTH = 1160;
const VIDEO_HEIGHT = 1456;

interface Mix {
  mixTitle: string;
  mixArweaveURL: string;
  mixDateYear: string;
  mixDuration: string;
  mixImageFilename: string;
  mixDescription: string;
}

interface Artist {
  artistName: string;
  artistFilename: string;
  artistImageFilename: string;
  artistGenre: string;
  artistBio: string;
  mixes: Mix[];
}

// Get random artist and their information
function getRandomArtist(): Artist {
  const artistsPath = path.join(process.cwd(), 'assets/artists.json');
  const artistsData = JSON.parse(fs.readFileSync(artistsPath, 'utf-8'));
  return artistsData[Math.floor(Math.random() * artistsData.length)];
}

// Get artist thumbnail path
function getArtistThumbnailPath(artistImageFilename: string): string {
  // Convert from img/artists/name.jpg to assets/artist_thumbnails/name.jpg
  const filename = path.basename(artistImageFilename);
  return path.join(process.cwd(), 'assets/artist_thumbnails', filename);
}

async function createPreviewVideo() {
  console.log('🚀 Starting quick preview test...');
  console.log('🎬 Creating quick preview video...');

  try {
    // Get random artist
    const artist = getRandomArtist();
    console.log(`Selected artist: ${artist.artistName}`);
    
    // Generate image prompt based on artist's genre
    const prompt = `Generate a dark, atmospheric underground electronic music scene for ${artist.artistGenre}. 
    Style: Underground club aesthetic, authentic ${artist.artistGenre.toLowerCase()} atmosphere
    Elements: DJ booth, dance floor, minimal lighting, authentic club environment
    Mood: Underground, energetic, authentic
    Color scheme: Deep blacks, industrial grays, accent neon highlights matching ${artist.artistGenre} vibe
    Theme: Underground Existence - Featuring ${artist.artistName} - ${artist.artistGenre}`;
    
    console.log('Generating image 1/1...');
    const imageUrls = await generateImages(prompt);
    
    if (!imageUrls || imageUrls.length === 0) {
      throw new Error('No images were generated');
    }

    console.log('Downloading generated image...');
    const imageUrl = imageUrls[0];
    
    // Handle both URLs and local file paths
    let imageBuffer: Buffer;
    if (imageUrl.startsWith('http')) {
      const response = await fetch(imageUrl);
      const arrayBuffer = await response.arrayBuffer();
      imageBuffer = Buffer.from(arrayBuffer);
    } else {
      imageBuffer = await fs.promises.readFile(imageUrl);
    }
    
    // Ensure output directories exist
    await fs.promises.mkdir('output/scenes', { recursive: true });
    await fs.promises.mkdir('output/preview', { recursive: true });
    
    // Save the background image
    const backgroundImagePath = path.join(process.cwd(), 'output/scenes/section_0_branded.png');
    await fs.promises.writeFile(backgroundImagePath, imageBuffer);

    // Get artist thumbnail path
    const thumbnailPath = getArtistThumbnailPath(artist.artistImageFilename);
    console.log(`Using thumbnail: ${path.basename(thumbnailPath)}`);

    // Verify thumbnail exists
    if (!fs.existsSync(thumbnailPath)) {
      throw new Error(`Artist thumbnail not found: ${thumbnailPath}`);
    }

    // Create the video with FFmpeg
    console.log('Executing FFmpeg command...');
    console.log('Using background image:', backgroundImagePath);
    console.log('Using thumbnail:', thumbnailPath);
    
    const outputPath = path.join(process.cwd(), 'output/preview', `preview_${artist.artistName.replace(/\s+/g, '_')}_${Date.now()}.mp4`);
    const ffmpegCommand = `ffmpeg -y \
      -i "${backgroundImagePath}" \
      -i "${thumbnailPath}" \
      -filter_complex " \
        [0:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1:1[bg]; \
        [bg]zoompan=z='1+0.1*t/8':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}[zoomed_bg]; \
        [1:v]scale=${Math.floor(VIDEO_WIDTH * 0.8)}:-1,format=rgba[scaled_thumb]; \
        [scaled_thumb]fade=in:st=0:d=1[faded_thumb]; \
        [zoomed_bg][faded_thumb]overlay=x='(W-w)/2':y='100'[with_thumb]; \
        [with_thumb]drawtext=fontfile=/System/Library/Fonts/Supplemental/Courier New Bold.ttf: \
        text='${artist.artistName}\\n${artist.artistGenre}': \
        fontsize=40:fontcolor=white: \
        x=(w-text_w)/2:y=h-h/4: \
        box=1:boxcolor=black@0.5:boxborderw=5: \
        alpha='if(lt(t,1),t,if(lt(t,7),1,1-(t-7)))'[out]" \
      -map "[out]" \
      -c:v libx264 \
      -t 8 \
      -pix_fmt yuv420p \
      "${outputPath}"`;

    console.log('FFmpeg filter chain:');
    console.log('1. Scale background');
    console.log('2. Apply zoom effect to background');
    console.log('3. Scale thumbnail to 80% width');
    console.log('4. Add fade-in effect to thumbnail');
    console.log('5. Overlay thumbnail on background');
    console.log('6. Add text overlay');

    await execAsync(ffmpegCommand);
    console.log('✅ Preview video created successfully!');
    console.log(`📁 Output file: ${outputPath}`);
    console.log(`🎵 Artist: ${artist.artistName} (${artist.artistGenre})`);
    console.log(`🎧 Available mixes: ${artist.mixes.length}`);
  } catch (error) {
    console.error('❌ Error creating preview video:', error);
    throw error;
  }
}

// Run the test if this file is executed directly
if (require.main === module) {
  console.log('🚀 Starting quick preview test...');
  createPreviewVideo()
    .then(() => {
      console.log('✨ Test completed successfully!');
    })
    .catch(error => {
      console.error('❌ Test failed:', error);
      process.exit(1);
    });
} 