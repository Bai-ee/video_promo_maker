import { config } from 'dotenv';
import { generateScript } from "./lib/gpt";
import { generateImages } from "./lib/images";
import { generateAudio } from "./lib/audio";
import { stitchVideo } from "./lib/video";
import * as fs from 'fs';

// Load environment variables
config();

// Create output directory if it doesn't exist
if (!fs.existsSync('./output')) {
  fs.mkdirSync('./output', { recursive: true });
}

// Verify API key is available
if (!process.env.OPENAI_API_KEY) {
  console.error("Error: OPENAI_API_KEY is not set in environment variables.");
  console.log("Please check your .env file and make sure it contains:");
  console.log("OPENAI_API_KEY=your_openai_api_key_here");
  process.exit(1);
}

async function createVideoFromPrompt(prompt: string) {
  console.log(`Generating script from prompt: "${prompt}"...`);
  const script = await generateScript(prompt);
  console.log("Script generated!");
  
  console.log("Generating images...");
  const images = await generateImages(script);
  console.log(`${images.length} images generated!`);
  
  console.log("Generating audio...");
  const audio = await generateAudio(script);
  console.log("Audio generated!");
  
  console.log("Stitching video...");
  try {
    const videoPath = await stitchVideo(images, audio);
    console.log("Video successfully created!");
    return videoPath;
  } catch (error) {
    console.error("Error creating video:", error);
    return null;
  }
}

createVideoFromPrompt("How AI is changing music production")
  .then(path => {
    if (path) {
      console.log(`Final video available at: ${path}`);
    } else {
      console.log("Video creation failed. Check logs for details.");
    }
  })
  .catch(error => console.error("Error creating video:", error)); 