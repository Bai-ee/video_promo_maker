import { loadArtists, Artist } from '../lib/artists';
import { createArtistVideo } from '../lib/renderers/video-renderer';
import { getBrandStyle } from '../lib/brand';
import { loadTemplate } from '../lib/templates';
import path from 'path';

async function main() {
  try {
    const artistName = process.argv[2];
    if (!artistName) {
      console.error('Please provide an artist name');
      process.exit(1);
    }

    // Load artist data
    const artists = await loadArtists();
    const artist = artists.find((a: Artist) => a.name === artistName);
    if (!artist) {
      console.error(`Artist "${artistName}" not found`);
      process.exit(1);
    }

    // Select a random mix
    const mix = artist.mixes[Math.floor(Math.random() * artist.mixes.length)];
    if (!mix) {
      console.error(`No mixes found for artist "${artistName}"`);
      process.exit(1);
    }

    // Load template and brand style
    const template = await loadTemplate('artist-promo');
    const brandStyle = getBrandStyle();

    // Create output path
    const outputPath = path.join(
      process.cwd(),
      'output',
      `artist-promo_${Date.now()}.mp4`
    );

    // Create video
    console.log(`Creating promo video for ${artistName}...`);
    const finalVideo = await createArtistVideo({
      artist,
      mix,
      template,
      brandStyle,
      outputPath
    });

    console.log(`Video created successfully at: ${finalVideo}`);
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main(); 