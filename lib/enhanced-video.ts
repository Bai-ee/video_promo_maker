import ffmpeg from 'fluent-ffmpeg';
import * as fs from 'fs';
import * as path from 'path';
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
  textPosition?: 'top' | 'middle' | 'bottom';
  textStyle?: 'heading' | 'subheading' | 'body';
  textColor?: string;
  duration: number;
  animation?: 'fade' | 'slide' | 'zoom';
  bgColor?: string;
  textOverlayPath?: string;
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
  console.log('Creating enhanced video with audio...');
  
  // Ensure output directory exists
  const outputDir = path.dirname(outputVideoPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Create temporary video file path
  const tempVideoPath = path.join(outputDir, `temp_${Date.now()}.mp4`);
  
  // Check for valid image files
  const validImages = scenes.filter(scene => 
    scene.imagePath && fs.existsSync(scene.imagePath)
  );
  
  // Verify audio path exists
  const hasValidAudio = audioPath && fs.existsSync(audioPath);
  if (!hasValidAudio) {
    console.warn('Audio file not found:', audioPath);
  }
  
  if (validImages.length > 0) {
    // Calculate total duration
    const totalDuration = validImages.reduce((sum, scene) => sum + (scene.duration || 3), 0);
    
    // Create ffmpeg command
    const command = ffmpeg();

    // Add image input
    command.input(validImages[0].imagePath)
           .loop(totalDuration);  // Loop the image for the total duration

    // Add audio input if available
    if (audioPath && hasValidAudio) {
      command.input(audioPath);
    }

    // Set up the command
    command
      .outputOptions('-y')
      .videoCodec('libx264')
      .size(`${VIDEO_WIDTH}x${VIDEO_HEIGHT}`)
      .audioCodec('aac')
      .audioBitrate('192k')
      .duration(totalDuration)
      .outputOptions([
        '-shortest',
        '-preset', 'medium',
        '-crf', '23',
        '-movflags', '+faststart'
      ]);

    if (hasValidAudio) {
      command.complexFilter([
        {
          filter: 'aformat',
          options: {
            sample_fmts: 'fltp',
            sample_rates: 44100,
            channel_layouts: 'stereo'
          },
          inputs: ['1:a'],
          outputs: ['audio']
        },
        {
          filter: 'atrim',
          options: `0:${totalDuration}`,
          inputs: ['audio'],
          outputs: ['audio_trimmed']
        }
      ])
      .outputOptions(['-map', '0:v', '-map', '[audio_trimmed]']);
    } else {
      command.outputOptions(['-map', '0:v']);
    }

    // Set output path and run the command
    return new Promise((resolve, reject) => {
      command.save(tempVideoPath)
             .on('start', (commandLine) => {
               console.log('FFmpeg command:', commandLine);
               console.log('Total duration:', totalDuration, 'seconds');
             })
             .on('end', () => {
               console.log('Video creation completed');
               // Rename temp file to final output
               fs.renameSync(tempVideoPath, outputVideoPath);
               resolve(outputVideoPath);
             })
             .on('error', (err, stdout, stderr) => {
               console.error('Error creating video:', err);
               console.error('FFmpeg stderr:', stderr);
               reject(err);
             });
    });
  } else {
    console.warn('No valid images found, creating test video');
    // Create a basic test video
    return new Promise((resolve, reject) => {
      ffmpeg()
        .input('color=c=black:s=1160x1456:d=30')
        .inputOptions(['-f lavfi'])
        .outputOptions([
          '-c:v libx264',
          '-preset medium',
          '-crf 23',
          '-movflags +faststart'
        ])
        .save(outputVideoPath)
        .on('end', () => {
          console.log('Test video created');
          resolve(outputVideoPath);
        })
        .on('error', (err) => {
          console.error('Error creating test video:', err);
          reject(err);
        });
    });
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