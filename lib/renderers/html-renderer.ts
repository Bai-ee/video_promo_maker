import * as fs from 'fs';
import * as path from 'path';
import * as Handlebars from 'handlebars';
import puppeteer from 'puppeteer';
import { BrandStyle } from '../brand';

export interface RenderOptions {
  template: string;
  data: Record<string, any>;
  outputPath: string;
  width: number;
  height: number;
  animationDuration?: number;
  brandStyle?: BrandStyle;
}

export async function renderTextToImage(options: RenderOptions): Promise<string> {
  const {
    template,
    data,
    outputPath,
    width,
    height,
    animationDuration = 1000,
    brandStyle
  } = options;

  // Ensure output directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Read and compile template
  const templateContent = fs.readFileSync(template, 'utf-8');
  const compiledTemplate = Handlebars.compile(templateContent);

  // Render template with data
  const html = compiledTemplate({
    ...data,
    width,
    height,
    animationDuration,
    brandStyle
  });

  // Launch browser and create page
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width, height });
    await page.setContent(html, { waitUntil: 'networkidle0' });

    // Wait for animations to complete
    await page.waitForTimeout(animationDuration);

    // Take screenshot
    await page.screenshot({
      path: outputPath,
      type: 'png',
      omitBackground: true
    });

    return outputPath;
  } finally {
    await browser.close();
  }
} 