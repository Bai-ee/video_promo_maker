import { renderTextToImage } from '../lib/renderers/html-renderer';
import { loadBrandStyle } from '../lib/brand';
import { AudioProcessor } from '../lib/audio-processor';
import fs from 'fs';
import path from 'path';

interface Artist {
  artistName: string;
  artistGenre: string;
  mixes: Array<{
    mixTitle: string;
    mixArweaveURL: string;
    mixDuration: string;
  }>;
}

async function loadArtists(): Promise<Artist[]> {
  const artistsPath = path.join(process.cwd(), 'assets', 'artists.json');
  const artistsData = fs.readFileSync(artistsPath, 'utf-8');
  return JSON.parse(artistsData);
}

async function getRandomMix(artists: Artist[]): Promise<{ 
  artist: Artist; 
  mix: Artist['mixes'][0];
}> {
  const randomArtist = artists[Math.floor(Math.random() * artists.length)];
  const randomMix = randomArtist.mixes[Math.floor(Math.random() * randomArtist.mixes.length)];
  return { artist: randomArtist, mix: randomMix };
}

async function testHtmlRenderer() {
  try {
    // Load brand style
    const brandStyle = loadBrandStyle();

    // Create test directories if they don't exist
    const testOutputDir = './output/test';
    if (!fs.existsSync(testOutputDir)) {
      fs.mkdirSync(testOutputDir, { recursive: true });
    }

    // Load artists and get a random mix
    const artists = await loadArtists();
    const { artist, mix } = await getRandomMix(artists);

    // Process audio
    console.log('Processing audio from mix:', mix.mixTitle);
    const audioResult = await AudioProcessor.processAudioUrl(mix.mixArweaveURL, 30);
    console.log(`Created ${audioResult.duration}s clip starting at ${audioResult.startTime}s`);

    // Read the template
    const templatePath = path.join(process.cwd(), 'templates/html/intro-slide.html');
    const template = fs.readFileSync(templatePath, 'utf-8');

    // Test data with mix information
    const testData = {
      artistName: artist.artistName,
      artistGenre: artist.artistGenre,
      mixTitle: mix.mixTitle,
      mixDuration: mix.mixDuration
    };

    // Render the image
    console.log('Rendering test image...');
    const outputPath = path.join(testOutputDir, 'test_render.png');
    await renderTextToImage({
      template,
      data: testData,
      outputPath,
      width: 1160,
      height: 1456,
      brandStyle
    });

    console.log(`Test image created at: ${outputPath}`);
    console.log(`Audio clip created at: ${audioResult.clipPath}`);

    // Clean up audio clip
    await AudioProcessor.cleanupClip(audioResult.clipPath);
  } catch (error) {
    console.error('Test failed:', error);
    throw error;
  }
}

// Run the test
testHtmlRenderer(); 