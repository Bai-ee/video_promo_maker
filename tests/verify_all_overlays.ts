import { existsSync, mkdirSync } from 'fs';
import path from 'path';
import sharp from 'sharp';
import { generateTextOverlay } from '../lib/text-overlay';
import { loadBrandStyle } from '../lib/brand';

interface TestArtist {
  name: string;
  genre: string;
  mixTitle: string;
  mixDuration: string;
  thumbnailPath: string;
}

async function generateAndVerifyOverlays(artist: TestArtist) {
  console.log(`\nTesting overlays for artist: ${artist.name}`);
  console.log('=====================================');

  // Ensure output directory exists
  const outputDir = './output/test_overlays';
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const brandStyle = loadBrandStyle();
  const width = 1160;
  const height = 1456;

  // 1. Generate placeholder background images
  console.log('\nGenerating background images...');
  try {
    const gradients = [
      { start: { r: 20, g: 20, b: 40 }, end: { r: 60, g: 60, b: 100 } },
      { start: { r: 40, g: 20, b: 20 }, end: { r: 100, g: 60, b: 60 } },
      { start: { r: 20, g: 40, b: 20 }, end: { r: 60, g: 100, b: 60 } }
    ];

    for (let i = 0; i < gradients.length; i++) {
      // Create a gradient background
      const gradient = gradients[i];
      const canvas = sharp({
        create: {
          width: width,
          height: height,
          channels: 4,
          background: { r: gradient.start.r, g: gradient.start.g, b: gradient.start.b, alpha: 1 }
        }
      });

      // Add some visual interest with a gradient overlay
      const svgGradient = `
        <svg width="${width}" height="${height}">
          <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:rgb(${gradient.start.r},${gradient.start.g},${gradient.start.b});stop-opacity:1" />
              <stop offset="100%" style="stop-color:rgb(${gradient.end.r},${gradient.end.g},${gradient.end.b});stop-opacity:1" />
            </linearGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#grad)" />
          <rect width="100%" height="100%" fill="${brandStyle.imageFilters.overlayColor}" style="mix-blend-mode: overlay" />
        </svg>`;

      await canvas
        .composite([{
          input: Buffer.from(svgGradient),
          blend: 'over'
        }])
        .toFile(path.join(outputDir, `background_${i}.png`));
      
      console.log(`✓ Generated background_${i}.png`);
    }
  } catch (error) {
    console.error('❌ Error generating background images:', error);
    return false;
  }

  // 2. Generate and verify text overlays
  console.log('\nGenerating text overlays...');
  try {
    // First overlay: Artist name and genre
    await generateTextOverlay(
      artist.name,
      artist.genre.toUpperCase(),
      width,
      height,
      brandStyle,
      path.join(outputDir, 'text_overlay_0.png'),
      { fontSize: brandStyle.fontSize.heading, alignment: 'center' }
    );
    console.log('✓ Generated text_overlay_0.png');

    // Second overlay: Mix title
    await generateTextOverlay(
      `"${artist.mixTitle}"`,
      '',
      width,
      height,
      brandStyle,
      path.join(outputDir, 'text_overlay_1.png'),
      { fontSize: brandStyle.fontSize.heading, alignment: 'center' }
    );
    console.log('✓ Generated text_overlay_1.png');

    // Third overlay: Brand and duration
    await generateTextOverlay(
      'Underground Existence',
      `${artist.mixDuration} Live Set`,
      width,
      height,
      brandStyle,
      path.join(outputDir, 'text_overlay_2.png'),
      { fontSize: brandStyle.fontSize.body, alignment: 'center' }
    );
    console.log('✓ Generated text_overlay_2.png');
  } catch (error) {
    console.error('❌ Error generating text overlays:', error);
    return false;
  }

  // 3. Generate and verify thumbnail composite
  console.log('\nGenerating thumbnail composites...');
  try {
    // Get artist thumbnail path
    const thumbnailPath = path.join('assets/artist_thumbnails', artist.thumbnailPath);
    if (!existsSync(thumbnailPath)) {
      console.error('❌ Artist thumbnail not found:', thumbnailPath);
      return false;
    }

    // Resize thumbnail
    const resizedArtistImage = await sharp(thumbnailPath)
      .resize(400, 400, {
        fit: 'cover',
        position: 'center'
      })
      .toBuffer();

    // Composite thumbnail onto each background
    for (let i = 0; i < 3; i++) {
      const bgPath = path.join(outputDir, `background_${i}.png`);
      if (existsSync(bgPath)) {
        await sharp(bgPath)
          .composite([
            {
              input: resizedArtistImage,
              top: 100,
              left: 380, // Centered: (1160 - 400) / 2 = 380
              gravity: 'center',
              blend: 'over'
            }
          ])
          .toFile(path.join(outputDir, `final_composite_${i}.png`));
        console.log(`✓ Generated final_composite_${i}.png`);
      }
    }
    
    return true;
  } catch (error) {
    console.error('❌ Error generating thumbnail composites:', error);
    return false;
  }
}

async function main() {
  // Test with AKILA's information
  const testArtist: TestArtist = {
    name: 'AKILA',
    genre: 'house',
    mixTitle: '...Head Ass!!!',
    mixDuration: '60:00',
    thumbnailPath: 'akila.jpg'
  };

  console.log('Starting overlay verification test...');
  const success = await generateAndVerifyOverlays(testArtist);

  if (success) {
    console.log('\n✓ All overlays generated successfully!');
    console.log('Check the output/test_overlays directory for:');
    console.log('  - background_[0-2].png (Generated background images)');
    console.log('  - text_overlay_[0-2].png (Text overlays)');
    console.log('  - final_composite_[0-2].png (Backgrounds with thumbnail)');
  } else {
    console.error('\n❌ Some overlays failed to generate');
  }
}

// Run the test
main().catch(console.error); 