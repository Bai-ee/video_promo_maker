import { writeFileSync } from "fs";
import { promisify } from "util";
import { exec } from "child_process";
import path from "path";

const execPromise = promisify(exec);

/**
 * Simplified audio generation - only creates silent audio
 * All text-to-speech functionality is disabled
 */
export async function generateAudio(script: string): Promise<string> {
  // Save the script to a text file (for reference only)
  const scriptPath = "./output/script.txt";
  writeFileSync(scriptPath, script);
  
  // Output path for the audio file
  const outputPath = "./output/audio.mp3";
  
  console.log("Skipping TTS, creating silent audio file...");
  
  try {
    // Generate a silent audio file using ffmpeg
    await execPromise(`ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -q:a 9 -acodec libmp3lame "${outputPath}"`);
    console.log("Created silent audio track");
    return outputPath;
  } catch (error) {
    console.error("Error creating silent audio:", error);
    // Create an empty file as last resort
    writeFileSync(outputPath, Buffer.alloc(1024));
    return outputPath;
  }
} 