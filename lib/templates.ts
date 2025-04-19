import { VideoTemplate } from './types';
import * as fs from 'fs/promises';
import * as path from 'path';

export type TemplateType = 'artist-promo' | 'product-demo' | 'tutorial-video';

export async function loadTemplate(type: TemplateType): Promise<VideoTemplate> {
  const templatePath = path.join(process.cwd(), 'templates', `${type}.json`);
  
  try {
    const templateContent = await fs.readFile(templatePath, 'utf-8');
    const template = JSON.parse(templateContent) as VideoTemplate;
    
    // Validate template structure
    if (!template.name || !template.sections || !Array.isArray(template.sections)) {
      throw new Error(`Invalid template structure in ${templatePath}`);
    }
    
    return template;
  } catch (error: any) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to load template ${type}: ${message}`);
  }
} 