import { execSync } from "child_process";
import { writeFileSync } from "fs";
import path from "path";

export async function stitchVideo(imagePaths: string[], audioPath: string): Promise<string> {
  // Make sure we have at least one image
  if (imagePaths.length === 0) {
    throw new Error("No images provided for video creation");
  }

  // Create a text file listing all images for ffmpeg
  const txtFile = "./output/images.txt";
  
  // Make sure paths in the text file are correct
  // Each line needs "file '[path]'" and "duration [seconds]"
  const fileContent = imagePaths.map(imagePath => {
    // Ensure we're using the full path and correct format
    const fullPath = path.resolve(imagePath);
    return `file '${fullPath}'\nduration 2`;
  }).join("\n");
  
  console.log(`Creating file list with ${imagePaths.length} images`);
  writeFileSync(txtFile, fileContent);
  
  // Debug: Print content of the images.txt file
  console.log("Contents of images.txt:");
  console.log(fileContent);

  // Create video from images
  const concatImages = "./output/concat.mp4";
  console.log("Running FFmpeg to create video from images...");
  try {
    execSync(`ffmpeg -y -f concat -safe 0 -i ${txtFile} -fps_mode vfr -pix_fmt yuv420p ${concatImages}`);
  } catch (error) {
    console.error("FFmpeg error when creating video from images:", error);
    throw error;
  }

  // Add audio to video
  const finalVideo = "./output/final_video.mp4";
  console.log("Adding audio to video...");
  try {
    execSync(`ffmpeg -y -i ${concatImages} -i ${audioPath} -c:v copy -c:a aac -shortest ${finalVideo}`);
  } catch (error) {
    console.error("FFmpeg error when adding audio to video:", error);
    throw error;
  }

  return finalVideo;
} 