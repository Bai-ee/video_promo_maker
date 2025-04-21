import ffmpeg from 'fluent-ffmpeg';
import ffmpegPath from 'ffmpeg-static';
import axios from 'axios';
import { createWriteStream } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';
import { promisify } from 'util';
import { unlink } from 'fs/promises';

console.log('FFmpeg Path:', ffmpegPath);

if (!ffmpegPath) {
  throw new Error('ffmpeg-static path not found');
}

ffmpeg.setFfmpegPath(ffmpegPath);
console.log('FFmpeg path set successfully');

interface AudioClipResult {
  clipPath: string;
  duration: number;
  startTime: number;
}

export class AudioProcessor {
  private static async downloadFile(url: string, outputPath: string): Promise<void> {
    console.log(`[AudioProcessor] Downloading file from ${url} to ${outputPath}`);
    const writer = createWriteStream(outputPath);
    const response = await axios({
      url,
      method: 'GET',
      responseType: 'stream'
    });

    console.log(`[AudioProcessor] Download response received, status: ${response.status}`);
    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
      writer.on('finish', () => {
        console.log(`[AudioProcessor] File download completed: ${outputPath}`);
        resolve();
      });
      writer.on('error', (error) => {
        console.error(`[AudioProcessor] Download error:`, error);
        reject(error);
      });
    });
  }

  private static async getAudioDuration(filePath: string): Promise<number> {
    console.log(`[AudioProcessor] Getting duration for file: ${filePath}`);
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (err, metadata) => {
        if (err) {
          console.error(`[AudioProcessor] Duration probe error:`, err);
          return reject(err);
        }
        const duration = metadata.format.duration || 0;
        console.log(`[AudioProcessor] Audio duration: ${duration} seconds`);
        resolve(duration);
      });
    });
  }

  private static async cutClip(
    inputPath: string,
    startTime: number,
    duration: number,
    outputPath: string,
    fadeInDuration: number = 2,
    fadeOutDuration: number = 2
  ): Promise<string> {
    console.log(`[AudioProcessor] Cutting clip:
      Input: ${inputPath}
      Start Time: ${startTime}
      Duration: ${duration}
      Output: ${outputPath}
      Fade In: ${fadeInDuration}s
      Fade Out: ${fadeOutDuration}s`);

    return new Promise((resolve, reject) => {
      ffmpeg(inputPath)
        .setStartTime(startTime)
        .duration(duration)
        .audioFilters([
          `afade=t=in:st=0:d=${fadeInDuration}`,
          `afade=t=out:st=${duration - fadeOutDuration}:d=${fadeOutDuration}`
        ])
        .output(outputPath)
        .on('start', (command) => {
          console.log(`[AudioProcessor] FFmpeg command: ${command}`);
        })
        .on('progress', (progress) => {
          console.log(`[AudioProcessor] Processing: ${progress.percent}% done`);
        })
        .on('end', () => {
          console.log(`[AudioProcessor] Clip cutting completed: ${outputPath}`);
          resolve(outputPath);
        })
        .on('error', (error) => {
          console.error(`[AudioProcessor] Clip cutting error:`, error);
          reject(error);
        })
        .run();
    });
  }

  public static async processAudioUrl(
    url: string,
    clipDuration: number = 30,
    fadeInDuration: number = 2,
    fadeOutDuration: number = 2
  ): Promise<AudioClipResult> {
    console.log(`[AudioProcessor] Starting audio processing:
      URL: ${url}
      Clip Duration: ${clipDuration}s
      Fade In: ${fadeInDuration}s
      Fade Out: ${fadeOutDuration}s`);

    const tempDir = tmpdir();
    const tempInput = join(tempDir, `${uuidv4()}.mp3`);
    const tempOutput = join(tempDir, `${uuidv4()}.mp3`);

    console.log(`[AudioProcessor] Temporary files:
      Input: ${tempInput}
      Output: ${tempOutput}`);

    try {
      // Download the file
      await this.downloadFile(url, tempInput);

      // Get duration
      const fullDuration = await this.getAudioDuration(tempInput);
      
      // Calculate random start time
      const maxStart = Math.max(0, fullDuration - clipDuration);
      const startTime = Math.floor(Math.random() * maxStart);
      console.log(`[AudioProcessor] Selected clip segment:
        Full Duration: ${fullDuration}s
        Max Start Time: ${maxStart}s
        Selected Start Time: ${startTime}s`);

      // Cut the clip with fades
      await this.cutClip(
        tempInput,
        startTime,
        clipDuration,
        tempOutput,
        fadeInDuration,
        fadeOutDuration
      );

      // Clean up input file
      await unlink(tempInput);
      console.log(`[AudioProcessor] Cleaned up input file: ${tempInput}`);

      console.log(`[AudioProcessor] Audio processing completed successfully`);
      return {
        clipPath: tempOutput,
        duration: clipDuration,
        startTime
      };
    } catch (error) {
      console.error(`[AudioProcessor] Processing error:`, error);
      // Clean up on error
      try {
        await unlink(tempInput);
        await unlink(tempOutput);
        console.log(`[AudioProcessor] Cleaned up temporary files after error`);
      } catch (cleanupError) {
        console.error(`[AudioProcessor] Cleanup error:`, cleanupError);
      }
      throw error;
    }
  }

  public static async cleanupClip(clipPath: string): Promise<void> {
    console.log(`[AudioProcessor] Cleaning up clip: ${clipPath}`);
    try {
      await unlink(clipPath);
      console.log(`[AudioProcessor] Clip cleaned up successfully`);
    } catch (error) {
      console.error(`[AudioProcessor] Cleanup error:`, error);
    }
  }
} 