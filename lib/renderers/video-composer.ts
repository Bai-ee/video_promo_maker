import ffmpeg from 'fluent-ffmpeg';
import path from 'path';
import fs from 'fs/promises';

export interface ComposeOptions {
  images: string[];
  audio?: string;
  outputPath: string;
  duration: number;
  width: number;
  height: number;
  fps?: number;
}

export async function composeVideo(options: ComposeOptions): Promise<string> {
  const {
    images,
    audio,
    outputPath,
    duration,
    width,
    height,
    fps = 30
  } = options;

  if (images.length === 0) {
    throw new Error('No images provided for video composition');
  }

  // Calculate duration per image
  const imageDuration = duration / images.length;
  
  // Ensure output directory exists
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  return new Promise((resolve, reject) => {
    let command = ffmpeg();

    // Add images as inputs
    images.forEach(image => {
      command = command.input(image);
    });

    // Add audio if provided
    if (audio) {
      command = command.input(audio);
    }

    // Build complex filter for image sequence
    const filters: string[] = [];
    const inputs: string[] = [];
    
    images.forEach((_, index) => {
      inputs.push(`[${index}:v]scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2[v${index}];`);
    });

    // Create the image sequence with transitions
    const sequence: string[] = [];
    images.forEach((_, index) => {
      sequence.push(`[v${index}]`);
    });
    
    // Concatenate all scaled inputs
    filters.push(
      ...inputs,
      `${sequence.join('')}concat=n=${images.length}:v=1:a=0[outv]`
    );

    // Set up the command
    command = command
      .complexFilter(filters, ['outv'])
      .outputOptions([
        `-t ${duration}`,
        `-r ${fps}`,
        '-pix_fmt yuv420p'
      ]);

    // Add audio if provided
    if (audio) {
      command = command.outputOptions([
        '-c:a aac',
        '-b:a 192k',
        '-shortest'
      ]);
    }

    // Set output
    command = command
      .output(outputPath)
      .on('end', () => resolve(outputPath))
      .on('error', (err) => reject(new Error(`Error composing video: ${err.message}`)));

    // Run the command
    command.run();
  });
} 