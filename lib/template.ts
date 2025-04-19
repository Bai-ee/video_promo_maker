import { BrandStyle, loadTemplate, fillTemplate } from './brand';
import sharp from 'sharp';
import path from 'path';
import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { generateImages } from './images';
import { generateScript } from './gpt';
import { generateAudio } from './audio';

interface VideoSection {
  type: string;
  duration: number;
  elements: any[];
}

interface VideoTemplate {
  templateName: string;
  templateType: string;
  scriptTemplate: string;
  sections: VideoSection[];
  audioOptions: any;
}

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
 * Process a template with user inputs and brand styling
 */
export async function processTemplate(
  templateType: string,
  userInputs: Record<string, any>,
  brandStyle: BrandStyle
): Promise<{ script: string; scenes: SceneConfig[]; audioPath: string }> {
  // Load and fill the template
  const template = loadTemplate(templateType) as VideoTemplate;
  const filledTemplate = fillTemplate(template, brandStyle, userInputs);
  
  // Generate the script based on the template
  const scriptPrompt = filledTemplate.scriptTemplate;
  console.log(`Generating script using prompt: ${scriptPrompt}`);
  const script = await generateScript(scriptPrompt);
  
  // Create scenes from the template sections
  const scenes: SceneConfig[] = [];
  
  // Ensure output directory exists
  const outputDir = './output/scenes';
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }
  
  // Process each section
  for (let i = 0; i < filledTemplate.sections.length; i++) {
    const section = filledTemplate.sections[i];
    
    // Handle different section types
    await processSection(section, i, scenes, outputDir, brandStyle);
  }
  
  // Generate audio with the full script
  const audioPath = await generateAudio(script);
  
  return {
    script,
    scenes,
    audioPath
  };
}

/**
 * Process a template section into scene configurations
 */
async function processSection(
  section: VideoSection,
  sectionIndex: number,
  scenes: SceneConfig[],
  outputDir: string,
  brandStyle: BrandStyle
): Promise<void> {
  // Determine background image/color and text elements
  let bgImage = '';
  let bgColor = '';
  let overlayText = '';
  let textPosition = 'center';
  let textStyle = {};
  let textColor = '#FFFFFF';
  let animation = 'none';
  
  // Process elements in the section
  for (const element of section.elements) {
    if (element.type === 'image' && element.prompt) {
      // Generate image using the provided prompt with brand styling
      const styledPrompt = `${element.prompt}, styled using ${brandStyle.primaryColor} and ${brandStyle.accentColor} color scheme, ${brandStyle.tone} feeling`;
      
      try {
        console.log(`Generating image for section ${sectionIndex} with prompt: ${styledPrompt}`);
        const images = await generateImages(styledPrompt);
        
        if (images && images.length > 0) {
          // Use the first image
          bgImage = images[0];
          
          // Apply brand-specific image processing if needed
          if (brandStyle.imageFilters) {
            // Create a processed version of the image with brand styling
            const processedPath = path.join(outputDir, `section_${sectionIndex}_branded.png`);
            
            // Apply filters using sharp
            await sharp(bgImage)
              .modulate({
                brightness: brandStyle.imageFilters.brightness,
                saturation: brandStyle.imageFilters.saturation
              })
              .convolve({
                width: 3,
                height: 3,
                kernel: [0, -0.5, 0, -0.5, 3, -0.5, 0, -0.5, 0]
              })
              .composite([{
                input: Buffer.from(`<svg><rect width="100%" height="100%" fill="${brandStyle.imageFilters.overlayColor}"/></svg>`),
                blend: 'overlay'
              }])
              .toFile(processedPath);
            
            bgImage = processedPath;
          }
        }
      } catch (error) {
        console.error('Error generating image for section:', error);
      }
    } else if (element.type === 'background' && element.color) {
      // Use specified background color
      bgColor = element.color;
    }
    
    if (element.type === 'text') {
      // Create overlay text
      overlayText = element.content || '';
      textPosition = element.position || 'center';
      
      // Apply text styling based on 'style' property
      if (element.style === 'heading') {
        textStyle = {
          fontSize: brandStyle.fontSize.heading,
          fontFamily: brandStyle.fontFamily,
          fontWeight: 'bold'
        };
      } else if (element.style === 'subheading') {
        textStyle = {
          fontSize: brandStyle.fontSize.subheading,
          fontFamily: brandStyle.fontFamily,
          fontWeight: 'normal'
        };
      } else if (element.style === 'body') {
        textStyle = {
          fontSize: brandStyle.fontSize.body,
          fontFamily: brandStyle.fontFamily,
          fontWeight: 'normal'
        };
      }
      
      // Use text color if specified
      textColor = element.color || textColor;
      
      // Use animation if specified
      animation = element.animation || animation;
    }
  }
  
  // Add the scene to the list
  scenes.push({
    imagePath: bgImage,
    overlayText,
    textPosition,
    textStyle,
    textColor,
    duration: section.duration || 3,
    animation,
    bgColor
  });
}

/**
 * Create lower third overlays for text
 * DISABLED to avoid SVG-related issues
 */
export function createLowerThird(
  text: string,
  outputPath: string,
  brandStyle: BrandStyle
): string {
  console.log('SVG functionality disabled - returning empty path');
  return '';
}

/**
 * Create intro frames with brand styling
 * DISABLED to avoid SVG-related issues
 */
export function createIntroFrame(
  text: string,
  outputPath: string,
  brandStyle: BrandStyle
): string {
  console.log('SVG functionality disabled - returning empty path');
  return '';
}

/**
 * Create outro frames with brand styling
 * DISABLED to avoid SVG-related issues
 */
export function createOutroFrame(
  callToAction: string,
  outputPath: string,
  brandStyle: BrandStyle
): string {
  console.log('SVG functionality disabled - returning empty path');
  return '';
} 