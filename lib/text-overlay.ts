import { createCanvas } from 'canvas';
import fs from 'fs';
import path from 'path';
import { BrandStyle } from './brand';

interface TextStyle {
  fontSize?: number;
  fontFamily?: string;
  color?: string;
  alignment?: 'left' | 'center' | 'right';
}

export function generateTextOverlay(
  text: string,
  subtext: string,
  width: number,
  height: number,
  brandStyle: BrandStyle,
  outputPath: string,
  textStyle?: TextStyle
) {
  // Create canvas
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  // Clear background to transparent
  ctx.clearRect(0, 0, width, height);

  // Set default text properties
  const defaultStyle = {
    fontSize: brandStyle.fontSize.heading,
    fontFamily: brandStyle.fontFamily,
    color: brandStyle.primaryColor,
    alignment: brandStyle.layout.textAlignment as TextStyle['alignment']
  };

  const style = { ...defaultStyle, ...textStyle };

  // Set text properties for main text
  ctx.font = `${style.fontSize}px ${style.fontFamily}`;
  ctx.fillStyle = style.color || '#FFFFFF';
  ctx.textAlign = style.alignment || 'center';
  ctx.textBaseline = 'middle';

  // Calculate maximum text width for wrapping
  const maxWidth = width * 0.8;

  // Wrap main text
  const words = text.split(' ');
  const lines = [];
  let currentLine = words[0];

  for (let i = 1; i < words.length; i++) {
    const word = words[i];
    const width = ctx.measureText(currentLine + " " + word).width;
    if (width < maxWidth) {
      currentLine += " " + word;
    } else {
      lines.push(currentLine);
      currentLine = word;
    }
  }
  lines.push(currentLine);

  // Calculate total height needed for text blocks
  const lineHeight = style.fontSize * 1.2;
  const subtextFontSize = brandStyle.fontSize.subheading;
  const subtextLineHeight = subtextFontSize * 1.2;
  const totalTextHeight = (lines.length * lineHeight) + (subtext ? subtextLineHeight + 20 : 0);

  // Calculate starting Y position to center text block vertically
  let currentY = (height - totalTextHeight) / 2;

  // Draw main text
  lines.forEach(line => {
    ctx.fillText(line, width / 2, currentY);
    currentY += lineHeight;
  });

  // Draw subtext if provided
  if (subtext) {
    ctx.font = `${subtextFontSize}px ${style.fontFamily}`;
    ctx.fillText(subtext, width / 2, currentY + 20);
  }

  // Ensure output directory exists
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // Write to file
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(outputPath, buffer);
} 