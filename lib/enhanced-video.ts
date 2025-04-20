import { execSync } from 'child_process';
import { writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import path from 'path';
import { BrandStyle } from './brand';
// Commenting out problematic imports
// import { createIntroFrame, createOutroFrame, createLowerThird } from './template';
// import { stitchVideo } from './video';

// Video dimensions
const VIDEO_WIDTH = 1160;
const VIDEO_HEIGHT = 1456;

interface SceneConfig {
  imagePath: string;
  overlayText?: string;
  textPosition?: string;
  textStyle?: any;
  textColor?: string;
  duration: number;
  animation?: string;
  bgColor?: string;
}

/**
 * Create a simplified video with multiple scenes - no complex features
 */
export async function createEnhancedVideo(
  scenes: SceneConfig[],
  audioPath: string,
  outputVideoPath: string,
  brandStyle: BrandStyle,
  callToAction: string = 'Get Started Today!'
): Promise<string> {
  console.log('\n=== Starting Video Creation Process ===');
  console.log('Output path:', outputVideoPath);
  
  // Ensure output directory exists
  const outputDir = path.dirname(outputVideoPath);
  if (!existsSync(outputDir)) {
    console.log('Creating output directory:', outputDir);
    mkdirSync(outputDir, { recursive: true });
  }
  
  const tmpDir = './output/tmp';
  if (!existsSync(tmpDir)) {
    console.log('Creating temporary directory:', tmpDir);
    mkdirSync(tmpDir, { recursive: true });
  }
  
  // Create temporary video file path
  const tempVideoPath = path.join(tmpDir, 'temp_video.mp4');
  
  // Check if we have all required overlay files
  console.log('\n=== Verifying Text Overlays ===');
  const requiredOverlays = ['text_overlay_0.png', 'text_overlay_1.png', 'text_overlay_2.png'];
  const scenesDir = './output/scenes';
  
  console.log('Checking scenes directory:', scenesDir);
  if (!existsSync(scenesDir)) {
    throw new Error('Scenes directory not found');
  }
  
  console.log('Required overlays:', requiredOverlays.join(', '));
  const missingOverlays = requiredOverlays.filter(overlay => {
    const exists = existsSync(path.join(scenesDir, overlay));
    console.log(`${overlay}: ${exists ? '✓ Found' : '✗ Missing'}`);
    return !exists;
  });
  
  if (missingOverlays.length > 0) {
    throw new Error(`Missing required text overlays: ${missingOverlays.join(', ')}`);
  }
  
  // Check if we have any valid image files
  console.log('\n=== Processing Image Files ===');
  let validImages: string[] = [];
  
  try {
    const allFiles = readdirSync(scenesDir);
    console.log('Total files in directory:', allFiles.length);
    
    validImages = allFiles
      .filter(file => {
        const isValid = file.endsWith('.png') || file.endsWith('.jpg');
        console.log(`${file}: ${isValid ? '✓ Valid' : '✗ Invalid'} format`);
        return isValid;
      })
      .sort((a, b) => {
        // Sort text overlays in correct order
        if (a.startsWith('text_overlay_') && b.startsWith('text_overlay_')) {
          return parseInt(a.match(/\d+/)?.[0] || '0') - parseInt(b.match(/\d+/)?.[0] || '0');
        }
        // Put background images before text overlays
        if (a.startsWith('text_overlay_')) return 1;
        if (b.startsWith('text_overlay_')) return -1;
        return a.localeCompare(b);
      })
      .map(file => path.join(scenesDir, file));
    
    console.log('\nProcessed images in order:');
    validImages.forEach((img, index) => {
      console.log(`${index + 1}. ${path.basename(img)}`);
    });
  } catch (error) {
    console.error('Error reading scenes directory:', error);
    throw error;
  }
  
  if (validImages.length > 0) {
    try {
      console.log('\n=== Creating Video ===');
      console.log('Number of images:', validImages.length);
      console.log('Duration per image:', `${30/validImages.length}s`);
      
      // Create a list of image inputs for ffmpeg
      const imageInputs = validImages.map(img => `-loop 1 -t ${30/validImages.length} -i "${img}"`).join(' ');
      
      console.log('Running FFmpeg for video creation...');
      // Create video from images with transitions
      execSync(`
        ffmpeg -y ${imageInputs} -filter_complex "
        ${validImages.map((_, i) => `[${i}:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1[v${i}]`).join(';')};
        ${validImages.map((_, i) => `[v${i}]`).join('')}concat=n=${validImages.length}:v=1:a=0[outv]
        " -map "[outv]" -c:v libx264 -pix_fmt yuv420p "${tempVideoPath}"
      `);
      
      console.log('\n=== Adding Audio ===');
      console.log('Audio file:', audioPath);
      // Add audio to the video
      execSync(`
        ffmpeg -y -i "${tempVideoPath}" -i "${audioPath}" -c:v copy -c:a aac -shortest "${outputVideoPath}"
      `);
      
      console.log('\n=== Video Creation Complete ===');
      console.log('Final video path:', outputVideoPath);
      return outputVideoPath;
    } catch (error) {
      console.error('\n=== Error Creating Video ===');
      console.error('Error details:', error);
      throw error;
    }
  }
  
  throw new Error('No valid images found for video creation');
}

/**
 * DISABLED: Add text overlays to scenes
 * This function is now commented out to avoid SVG related issues
 */
/*
async function addTextOverlays(
  scenes: SceneConfig[],
  outputDir: string,
  brandStyle: BrandStyle
): Promise<SceneConfig[]> {
  // Just return the original scenes without modification
  return scenes;
}
*/ 