import { readFileSync, existsSync, readdirSync } from 'fs';
import path from 'path';
import { VideoTemplate, VideoSection, VideoElement } from '../types/video';
import artistPromoTemplate from '../templates/artist-promo';

interface FontSize {
  heading: number;
  subheading: number;
  body: number;
  caption: number;
}

interface Layout {
  titlePosition: string;
  logoPosition: string;
  textAlignment: string;
}

interface VideoStyle {
  transitionType: string;
  transitionDuration: number;
  captionStyle: string;
  useLowerThirds: boolean;
  useIntro: boolean;
  useOutro: boolean;
  introDuration: number;
  outroDuration: number;
}

interface PromptTemplates {
  [key: string]: string;
}

interface ImageFilters {
  saturation: number;
  brightness: number;
  contrast: number;
  useOverlay: boolean;
  overlayColor: string;
  grain: boolean;
  blur: number;
  vignette: boolean;
}

export interface BrandStyle {
  brandName: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  backgroundColor: string;
  fontFamily: string;
  fontFamilyFallback: string;
  fontSize: FontSize;
  tone: string;
  voiceStyle: string;
  logoPath: string;
  useBorders: boolean;
  borderColor: string;
  borderWidth: number;
  layout: Layout;
  videoStyle: VideoStyle;
  promptTemplates: PromptTemplates;
  imageFilters: ImageFilters;
}

export interface PromoAsset {
  type: string;
  path: string;
  caption?: string;
  tags?: string[];
  dateCreated?: string;
}

/**
 * Loads brand style guide from JSON file
 */
export function loadBrandStyle(stylePath: string = './brand/style-guide.json'): BrandStyle {
  try {
    const styleContent = readFileSync(stylePath, 'utf-8');
    return JSON.parse(styleContent) as BrandStyle;
  } catch (error) {
    console.error('Error loading brand style guide:', error);
    throw new Error('Failed to load brand style guide');
  }
}

/**
 * Loads a specific template by type
 */
export function loadTemplate(templateType: string): VideoTemplate {
  try {
    const templateFile = path.join('./templates', `${templateType}.json`);
    
    if (existsSync(templateFile)) {
      console.log(`Loading template from ${templateFile}...`);
      const templateContent = readFileSync(templateFile, 'utf-8');
      const template = JSON.parse(templateContent) as VideoTemplate;
      
      // Validate template structure
      if (!template.templateName || !template.templateType || !template.scriptTemplate || !template.sections) {
        throw new Error(`Invalid template structure in ${templateFile}`);
      }
      
      console.log('Template structure:', {
        name: template.templateName,
        type: template.templateType,
        hasScript: !!template.scriptTemplate,
        sectionsCount: template.sections?.length
      });
      
      return template;
    }
    
    // Try to find a template with templateType in the name
    const files = readdirSync('./templates');
    for (const file of files) {
      if (file.includes(templateType) && file.endsWith('.json')) {
        const templateContent = readFileSync(path.join('./templates', file), 'utf-8');
        const template = JSON.parse(templateContent) as VideoTemplate;
        
        // Validate template structure
        if (!template.templateName || !template.templateType || !template.scriptTemplate || !template.sections) {
          throw new Error(`Invalid template structure in ${file}`);
        }
        
        return template;
      }
    }
    
    throw new Error(`Template for ${templateType} not found`);
  } catch (error) {
    console.error(`Error loading template for ${templateType}:`, error);
    throw error;
  }
}

/**
 * Catalogs promo assets from a directory
 */
export function getPromoAssets(assetDir: string = './assets/promo-history'): PromoAsset[] {
  const assets: PromoAsset[] = [];
  
  try {
    if (!existsSync(assetDir)) {
      console.warn(`Asset directory ${assetDir} does not exist`);
      return [];
    }
    
    const files = readdirSync(assetDir);
    
    for (const file of files) {
      const filePath = path.join(assetDir, file);
      const extension = path.extname(file).toLowerCase();
      
      let type = 'unknown';
      if (['.jpg', '.jpeg', '.png', '.gif'].includes(extension)) {
        type = 'image';
      } else if (['.mp4', '.mov', '.avi', '.webm'].includes(extension)) {
        type = 'video';
      } else if (['.mp3', '.wav', '.ogg'].includes(extension)) {
        type = 'audio';
      } else if (extension === '.txt') {
        type = 'text';
      }
      
      // Get associated caption if exists
      const baseName = path.basename(file, extension);
      const captionPath = path.join(assetDir, `${baseName}.txt`);
      let caption: string | undefined = undefined;
      
      if (type !== 'text' && existsSync(captionPath)) {
        caption = readFileSync(captionPath, 'utf-8');
      }
      
      assets.push({
        type,
        path: filePath,
        caption,
        tags: [], // Could be expanded to parse tags from filenames or metadata
        dateCreated: new Date().toISOString() // This could be replaced with actual file creation date
      });
    }
    
    return assets;
  } catch (error) {
    console.error('Error cataloging promo assets:', error);
    return [];
  }
}

/**
 * Apply brand styling to image generation prompts
 */
export function applyBrandStylingToPrompt(prompt: string, brandStyle: BrandStyle): string {
  // Add brand-specific styling to the image prompts
  return `${prompt}, in the style of ${brandStyle.brandName}, using ${brandStyle.primaryColor} and ${brandStyle.accentColor} color scheme, ${brandStyle.tone} feeling`;
}

/**
 * Fill a template with brand styling and user inputs
 */
export function fillTemplate(
  template: VideoTemplate,
  brandStyle: BrandStyle,
  userInputs: Record<string, any>
): VideoTemplate {
  // Validate inputs
  if (!template || !template.sections || !template.scriptTemplate) {
    throw new Error('Invalid template structure');
  }
  
  if (!brandStyle) {
    throw new Error('Brand style is required');
  }
  
  if (!userInputs) {
    throw new Error('User inputs are required');
  }

  // Create a deep copy of the template
  const filledTemplate: VideoTemplate = {
    templateName: template.templateName,
    templateType: template.templateType,
    scriptTemplate: replaceVariables(template.scriptTemplate, userInputs),
    sections: template.sections.map((section: VideoSection) => ({
      type: section.type,
      duration: section.duration,
      elements: section.elements.map((element: VideoElement) => ({
        ...element,
        content: element.content ? replaceVariables(element.content, userInputs) : undefined,
        prompt: element.prompt ? replaceVariables(element.prompt, userInputs) : undefined
      }))
    })),
    audioOptions: { ...template.audioOptions }
  };
  
  return filledTemplate;
}

/**
 * Replace variables in a string with user input values
 */
function replaceVariables(text: string, variables: Record<string, any>): string {
  return text.replace(/\{(\w+)\}/g, (match, key) => variables[key] || match);
} 