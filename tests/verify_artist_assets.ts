import { existsSync } from 'fs';
import path from 'path';
import sharp from 'sharp';

interface ArtistInfo {
  name: string;
  filename: string;
  thumbnailPath: string;
}

async function verifyArtistAsset(artist: ArtistInfo) {
  console.log(`\nVerifying assets for artist: ${artist.name}`);
  
  // Check if thumbnail exists
  const thumbnailPath = path.join('assets/artist_thumbnails', artist.thumbnailPath);
  if (!existsSync(thumbnailPath)) {
    console.error(`❌ Thumbnail not found: ${thumbnailPath}`);
    return false;
  }
  
  // Verify image dimensions and format
  try {
    const metadata = await sharp(thumbnailPath).metadata();
    console.log(`✓ Thumbnail found: ${artist.thumbnailPath}`);
    console.log(`  - Dimensions: ${metadata.width}x${metadata.height}`);
    console.log(`  - Format: ${metadata.format}`);
    console.log(`  - Size: ${(metadata.size || 0) / 1024}KB`);
    
    // Check if image is large enough to be resized to 400x400
    if ((metadata.width || 0) < 400 || (metadata.height || 0) < 400) {
      console.warn(`⚠️ Warning: Image is smaller than target size (400x400)`);
    }
    
    return true;
  } catch (error) {
    console.error(`❌ Error reading thumbnail: ${error}`);
    return false;
  }
}

async function main() {
  // List of artists to verify
  const artists: ArtistInfo[] = [
    { name: 'AKILA', filename: 'akila.html', thumbnailPath: 'akila.jpg' },
    { name: 'ANDREW EMIL', filename: 'andrew_emil.html', thumbnailPath: 'andrew_emil.jpg' },
    { name: 'BAI-EE', filename: 'bai-ee.html', thumbnailPath: 'bai-ee2.jpg' },
    { name: 'BERNARD BADIE', filename: 'bernardbadie.html', thumbnailPath: 'bernardbadie.jpg' },
    { name: 'CESAR RAMIREZ', filename: 'cesarramirez.html', thumbnailPath: 'cesarramirez.jpg' },
    { name: 'CHICAGA SKYWAY', filename: 'chickageskyway.html', thumbnailPath: 'chickageskyway.jpg' },
    { name: 'IKE', filename: 'ike.html', thumbnailPath: 'ike.jpg' },
    { name: 'JEVON JACKSON', filename: 'jevonjackson.html', thumbnailPath: 'jevonjackson.png' },
    { name: 'JOSH ZEITLER', filename: 'josh_zeitler.html', thumbnailPath: 'josh_zeitler.png' },
    { name: 'JS', filename: 'js.html', thumbnailPath: 'js.jpg' },
    { name: 'RED EYE', filename: 'redeye.html', thumbnailPath: 'redeye.png' },
    { name: 'SASSMOUTH', filename: 'sassmouth.html', thumbnailPath: 'sassmouth.jpg' },
    { name: 'SEAN SMITH', filename: 'sean_smith.html', thumbnailPath: 'sean_smith.jpg' },
    { name: 'STAR TRAXX', filename: 'startraxx.html', thumbnailPath: 'startraxxthumb.jpg' },
    { name: 'TYREL WILLIAMS', filename: 'tyrelwilliams.html', thumbnailPath: 'tyrelwilliams.jpg' }
  ];

  console.log('Starting asset verification...');
  console.log('===============================');

  let success = 0;
  let failed = 0;

  for (const artist of artists) {
    const result = await verifyArtistAsset(artist);
    if (result) {
      success++;
    } else {
      failed++;
    }
  }

  console.log('\nVerification Summary');
  console.log('===================');
  console.log(`Total artists: ${artists.length}`);
  console.log(`✓ Successful: ${success}`);
  console.log(`❌ Failed: ${failed}`);
}

// Run the verification
main().catch(console.error); 