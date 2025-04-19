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
  console.log('Creating video with audio...');
  
  // Ensure output directory exists
  const outputDir = path.dirname(outputVideoPath);
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }
  
  const tmpDir = './output/tmp';
  if (!existsSync(tmpDir)) {
    mkdirSync(tmpDir, { recursive: true });
  }
  
  // Create temporary video file path
  const tempVideoPath = path.join(tmpDir, 'temp_video.mp4');
  
  // Check if we have any valid image files
  console.log('Checking for valid images in output/scenes directory...');
  const scenesDir = './output/scenes';
  let validImages: string[] = [];
  
  if (existsSync(scenesDir)) {
    try {
      validImages = readdirSync(scenesDir)
        .filter(file => file.endsWith('.png') || file.endsWith('.jpg'))
        .map(file => path.join(scenesDir, file));
      
      console.log(`Found ${validImages.length} valid images`);
    } catch (error) {
      console.error('Error reading scenes directory:', error);
    }
  }
  
  if (validImages.length > 0) {
    try {
      console.log('Creating video from available images...');
      
      // Create a list of image inputs for ffmpeg
      const imageInputs = validImages.map(img => `-loop 1 -t ${30/validImages.length} -i "${img}"`).join(' ');
      
      // Create video from images with transitions
      execSync(`
        ffmpeg -y ${imageInputs} -filter_complex "
        ${validImages.map((_, i) => `[${i}:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1[v${i}]`).join(';')};
        ${validImages.map((_, i) => `[v${i}]`).join('')}concat=n=${validImages.length}:v=1:a=0[outv]
        " -map "[outv]" -c:v libx264 -pix_fmt yuv420p "${tempVideoPath}"
      `);
      
      console.log('Adding audio to video...');
      // Add audio to the video
      execSync(`
        ffmpeg -y -i "${tempVideoPath}" -i "${audioPath}" -c:v copy -c:a aac -shortest "${outputVideoPath}"
      `);
      
      console.log(`Video with audio created at: ${outputVideoPath}`);
      return outputVideoPath;
    } catch (error) {
      console.error('Error creating video:', error);
      throw error;
    }
  }
  
  // If we don't have valid images, create a basic test video with audio
  console.log('Creating basic test video pattern with audio...');
  try {
    // Create test video
    execSync(`
      ffmpeg -y -f lavfi -i testsrc=duration=30:size=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:rate=30 -c:v libx264 -pix_fmt yuv420p "${tempVideoPath}"
    `);
    
    // Add audio to the test video
    execSync(`
      ffmpeg -y -i "${tempVideoPath}" -i "${audioPath}" -c:v copy -c:a aac -shortest "${outputVideoPath}"
    `);
    
    console.log(`Test video with audio created at: ${outputVideoPath}`);
    return outputVideoPath;
  } catch (error) {
    console.error('Error creating test video:', error);
    throw new Error('Failed to create video');
  }
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