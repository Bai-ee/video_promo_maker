import { registerFont } from 'canvas';
import path from 'path';
import fs from 'fs';

// Font file extensions we support
const FONT_EXTENSIONS = ['.ttf', '.otf'];

/**
 * Register a font file with the canvas library
 */
export function registerCustomFont(fontPath: string, fontFamily: string) {
  if (!fs.existsSync(fontPath)) {
    throw new Error(`Font file not found: ${fontPath}`);
  }
  
  registerFont(fontPath, { family: fontFamily });
  console.log(`Registered font: ${fontFamily} from ${fontPath}`);
}

/**
 * Load all fonts from the fonts directory
 */
export function loadCustomFonts() {
  const fontsDir = path.join(process.cwd(), 'assets', 'fonts');
  
  // Create fonts directory if it doesn't exist
  if (!fs.existsSync(fontsDir)) {
    fs.mkdirSync(fontsDir, { recursive: true });
    console.log('Created fonts directory:', fontsDir);
    return;
  }
  
  // Read all font files and register them
  const fontFiles = fs.readdirSync(fontsDir)
    .filter(file => FONT_EXTENSIONS.some(ext => file.toLowerCase().endsWith(ext)));
    
  if (fontFiles.length === 0) {
    console.log('No font files found in:', fontsDir);
    return;
  }
  
  fontFiles.forEach(file => {
    const fontPath = path.join(fontsDir, file);
    const fontFamily = path.parse(file).name;
    registerCustomFont(fontPath, fontFamily);
  });
} 