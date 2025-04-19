import ffmpeg from 'fluent-ffmpeg';
import ffmpegPath from 'ffmpeg-static';
import axios from 'axios';
import { createWriteStream } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';
import { promisify } from 'util';
import { unlink } from 'fs/promises';

if (!ffmpegPath) {
  throw new Error('ffmpeg-static path not found');
}

ffmpeg.setFfmpegPath(ffmpegPath);

interface AudioClipResult {
  clipPath: string;
  duration: number;
  startTime: number;
}

export class AudioProcessor {
  private static async downloadFile(url: string, outputPath: string): Promise<void> {
    const writer = createWriteStream(outputPath);
    const response = await axios({
      url,
      method: 'GET',
      responseType: 'stream'
    });

    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
      writer.on('finish', resolve);
      writer.on('error', reject);
    });
  }

  private static async getAudioDuration(filePath: string): Promise<number> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (err, metadata) => {
        if (err) return reject(err);
        resolve(metadata.format.duration || 0);
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
    return new Promise((resolve, reject) => {
      ffmpeg(inputPath)
        .setStartTime(startTime)
        .duration(duration)
        .audioFilters([
          `afade=t=in:st=0:d=${fadeInDuration}`,
          `afade=t=out:st=${duration - fadeOutDuration}:d=${fadeOutDuration}`
        ])
        .output(outputPath)
        .on('end', () => resolve(outputPath))
        .on('error', reject)
        .run();
    });
  }

  public static async processAudioUrl(
    url: string,
    clipDuration: number = 30,
    fadeInDuration: number = 2,
    fadeOutDuration: number = 2
  ): Promise<AudioClipResult> {
    const tempDir = tmpdir();
    const tempInput = join(tempDir, `${uuidv4()}.mp3`);
    const tempOutput = join(tempDir, `${uuidv4()}.mp3`);

    try {
      // Download the file
      await this.downloadFile(url, tempInput);

      // Get duration
      const fullDuration = await this.getAudioDuration(tempInput);
      
      // Calculate random start time
      const maxStart = Math.max(0, fullDuration - clipDuration);
      const startTime = Math.floor(Math.random() * maxStart);

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

      return {
        clipPath: tempOutput,
        duration: clipDuration,
        startTime
      };
    } catch (error) {
      // Clean up on error
      try {
        await unlink(tempInput);
        await unlink(tempOutput);
      } catch {}
      throw error;
    }
  }

  public static async cleanupClip(clipPath: string): Promise<void> {
    try {
      await unlink(clipPath);
    } catch {}
  }
} 