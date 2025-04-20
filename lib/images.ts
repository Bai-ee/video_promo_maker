import { writeFileSync, existsSync, mkdirSync } from "fs";
import fetch from 'node-fetch';
import path from 'path';
import fs from 'fs';
import { createCanvas } from 'canvas';

// Debug log for API key
console.log('API Key length:', process.env.OPENAI_API_KEY?.length);
console.log('API Key prefix:', process.env.OPENAI_API_KEY?.substring(0, 10));

interface ImageGenerationResponse {
  data: Array<{
    url: string;
  }>;
}

interface StyleGuide {
  thumbnailStyleGuide: {
    description: string;
    characteristics: string[];
    aiPrompt: string;
  };
  subsonicArchive: {
    colorPalette: string[];
    textures: string[];
    composition: string[];
    typography: string[];
  };
}

function constructImagePrompt(baseScene: string, styleGuide: StyleGuide): string {
  // Get current timestamp for metadata
  const timestamp = new Date().toISOString().split('T')[0];
  const catalogId = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
  
  // Core aesthetic foundation
  const aestheticBase = `Create a scene that embodies a Blade Runner meets Boiler Room aesthetic. 
The image should feel like a recovered artifact from an underground music archive. `;
  
  // Color palette specification
  const colorSpec = `Use a stark color palette:
- Primary: jet black, asphalt grey, midnight navy
- Accent: holographic neon (hot magenta, chrome green, purple haze)
- Highlight: tape-burn orange and dusty pink for archival contrast
Ensure deep shadows and high contrast lighting with stark backlighting or neon bleed. `;
  
  // Texture and composition layers
  const textureSpec = `Apply multiple texture layers:
1. Base: Kodak 400TX style grain structure
2. Overlay: VHS static and vinyl record scratches
3. Surface: Rusted steel grunge and analog distortion
4. Edge: Subtle vignette with light leak effects `;
  
  const compositionSpec = `Frame the composition using:
- Wide-angle urban isolation (1-point perspective)
- Low angles with dramatic spotlight focus
- Industrial architecture elements
- Subjects silhouetted against neon sources `;
  
  // Technical overlay elements
  const metadataOverlay = `Include IBM Plex Mono typography overlays:
[ARCHIVE MODE ENGAGED]
CAT${catalogId}-UE
DATADUMP: ${timestamp}
SECTOR 7F — NIGHT AUDIO `;
  
  // Scene-specific enhancements
  const enhancedScene = `Core scene: ${baseScene}
Additional elements:
- Scanned object layering
- Horizontal VHS tracking bars
- Night vision/thermal filter hints
- Metadata timestamp burn-ins `;
  
  // Final composition
  return `${aestheticBase}
${colorSpec}
${textureSpec}
${compositionSpec}
${enhancedScene}
${metadataOverlay}
Technical requirements: Ensure high contrast, cinematic composition with strong emphasis on lighting and atmosphere. The final image should feel like a recovered artifact from an underground archive.`;
}

export async function generateImages(script: string): Promise<string[]> {
  // Ensure output directories exist
  const outputDir = "./output";
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }
  
  const scenesDir = "./output/scenes";
  if (!existsSync(scenesDir)) {
    mkdirSync(scenesDir, { recursive: true });
  }

  const imagePaths: string[] = [];
  
  try {
    // Load style guide
    const styleGuide = JSON.parse(fs.readFileSync('./config/thumbnail_style_guide.json', 'utf8')) as StyleGuide;
    
    // Generate scene descriptions based on the script
    const scenes = [
      "A hyperrealistic 4K professional photograph of a dark Chicago warehouse interior in the 90s. No perceivable people, only silhouettes and fog, lit by strobing light and ambient haze. Industrial, analog textures. Cinematic realism.",
      "Close-up of vintage mixer knobs and faders, bathed in tape-burn orange light, with a blurred crowd of dancer silhouettes in the background",
      "Wide-angle shot of an underground archive room, dusty light beams revealing rows of vinyl records, with holographic catalog numbers floating in the air"
    ];
    
    // Generate images using OpenAI's image generation API
    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      const imagePath = path.join(scenesDir, `section_${i}_branded.png`);
      
      try {
        console.log(`Generating image ${i + 1}/${scenes.length}...`);
        
        // Construct enhanced prompt with Subsonic Archive style
        const fullPrompt = constructImagePrompt(scene, styleGuide);
        
        const response = await fetch("https://api.openai.com/v1/images/generations", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "dall-e-3",
            prompt: fullPrompt,
            n: 1,
            size: "1024x1024",
            quality: "hd",
            style: "vivid"
          })
        });

        if (!response.ok) {
          throw new Error(`API Error (${response.status}): ${await response.text()}`);
        }

        const data = await response.json() as ImageGenerationResponse;
        const imageUrl = data.data[0].url;

        // Download and save the image
        console.log(`Downloading generated image...`);
        const imgRes = await fetch(imageUrl);
        
        if (!imgRes.ok) {
          throw new Error(`Failed to download image: ${imgRes.status}`);
        }
        
        const buffer = await imgRes.arrayBuffer();
        writeFileSync(imagePath, Buffer.from(buffer));
        imagePaths.push(imagePath);
        
      } catch (error) {
        console.error(`Error generating image ${i + 1}:`, error);
        // Create fallback image
        const canvas = createCanvas(1024, 1024);
        const ctx = canvas.getContext('2d');
        
        // Fill background with gradient
        const gradient = ctx.createLinearGradient(0, 0, 1024, 1024);
        gradient.addColorStop(0, '#1a1a1a');
        gradient.addColorStop(1, '#2a2a2a');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 1024, 1024);
        
        // Add some visual interest
        ctx.strokeStyle = '#8B5CF6';
        ctx.lineWidth = 2;
        for (let j = 0; j < 10; j++) {
          ctx.beginPath();
          ctx.moveTo(0, j * 100);
          ctx.lineTo(1024, j * 100);
          ctx.stroke();
        }
        
        writeFileSync(imagePath, canvas.toBuffer());
        imagePaths.push(imagePath);
      }
    }
  } catch (error) {
    console.error("Error in image generation process:", error);
    const fallbackPath = path.join(scenesDir, "scene_fallback.png");
    const canvas = createCanvas(1024, 1024);
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, 1024, 1024);
    writeFileSync(fallbackPath, canvas.toBuffer());
    imagePaths.push(fallbackPath);
  }

  return imagePaths;
} 