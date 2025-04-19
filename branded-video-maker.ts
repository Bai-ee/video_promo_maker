import { config } from 'dotenv';
import { loadBrandStyle, getPromoAssets } from './lib/brand';
import { processTemplate } from './lib/template';
import { createEnhancedVideo } from './lib/enhanced-video';
import { AudioProcessor } from './lib/audio-processor';
import path from 'path';
import { existsSync, mkdirSync, readFileSync } from 'fs';

// Load environment variables
config();

// Check for OpenAI API key
if (!process.env.OPENAI_API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is not set.');
  console.log('Please add your API key to the .env file.');
  process.exit(1);
}

interface ArtistData {
  artistName: string;
  artistFilename: string;
  artistImageFilename: string;
  artistGenre: string;
  artistBio: string;
  mixes: Array<{
    mixTitle: string;
    mixArweaveURL: string;
    mixDateYear: string;
    mixDuration: string;
    mixImageFilename: string;
    mixDescription: string;
  }>;
}

function loadArtistData(artistName: string): ArtistData | null {
  try {
    const artistsData = JSON.parse(readFileSync('./assets/artists.json', 'utf-8'));
    return artistsData.find((artist: ArtistData) => 
      artist.artistName.toLowerCase() === artistName.toLowerCase()
    );
  } catch (error) {
    console.error('Error loading artist data:', error);
    return null;
  }
}

function getRandomMix(artist: ArtistData) {
  const mixIndex = Math.floor(Math.random() * artist.mixes.length);
  return artist.mixes[mixIndex];
}

/**
 * Create a branded video based on a template and user inputs
 */
async function createBrandedVideo(
  templateType: string, 
  userInputs: Record<string, any>,
  outputPath: string = './output/branded_video.mp4',
  audioUrl?: string
): Promise<string> {
  let audioClip: { clipPath: string; duration: number; startTime: number } | undefined;
  
  try {
    console.log(`Creating branded video using ${templateType} template...`);
    
    // Handle artist-specific processing
    if (templateType === 'artist-promo' && userInputs.artistName) {
      console.log(`Loading data for artist: ${userInputs.artistName}`);
      const artistData = loadArtistData(userInputs.artistName);
      
      if (!artistData) {
        throw new Error(`Artist "${userInputs.artistName}" not found in database`);
      }

      const selectedMix = getRandomMix(artistData);
      audioUrl = selectedMix.mixArweaveURL;
      
      // Update user inputs with artist data
      userInputs = {
        ...userInputs,
        artistName: artistData.artistName,
        artistGenre: artistData.artistGenre,
        mixTitle: selectedMix.mixTitle,
        mixDescription: selectedMix.mixDescription,
        artistImage: artistData.artistImageFilename,
        callToAction: 'Listen to more mixes at Underground Existence'
      };
    }
    
    // Ensure output directory exists
    const outputDir = path.dirname(outputPath);
    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }
    
    // Load brand styling
    console.log('Loading brand style guide...');
    const brandStyle = loadBrandStyle();
    
    // Process audio if URL provided
    if (audioUrl) {
      console.log('Processing audio clip...');
      audioClip = await AudioProcessor.processAudioUrl(audioUrl);
      console.log(`Created ${audioClip.duration}s clip starting at ${audioClip.startTime}s`);
    }
    
    // Catalog existing promo assets (if needed for reference)
    console.log('Cataloging existing promo assets...');
    const promoAssets = getPromoAssets();
    console.log(`Found ${promoAssets.length} existing promo assets.`);
    
    // Process the template to generate script and scenes
    console.log('Processing template...');
    const { script, scenes, audioPath } = await processTemplate(
      templateType,
      userInputs,
      brandStyle
    );
    
    console.log(`Generated script (${script.length} characters) and ${scenes.length} scenes.`);
    
    // Create the final video with all brand styling
    console.log('Creating final video with brand styling...');
    const finalVideoPath = await createEnhancedVideo(
      scenes,
      audioClip?.clipPath || audioPath,
      outputPath,
      brandStyle,
      userInputs.callToAction || 'Visit our website!'
    );
    
    // Clean up audio clip if it was created
    if (audioClip) {
      await AudioProcessor.cleanupClip(audioClip.clipPath);
    }
    
    console.log('✅ Branded video created successfully!');
    console.log(`Output: ${finalVideoPath}`);
    
    return finalVideoPath;
  } catch (error) {
    // Clean up audio clip on error
    if (audioClip) {
      await AudioProcessor.cleanupClip(audioClip.clipPath);
    }
    console.error('Error creating branded video:', error);
    throw error;
  }
}

// Example usage
// Define the user inputs for a product announcement
const productAnnouncement = {
  productName: 'Pixel Quest Adventures',
  productDescription: 'an immersive 8-bit role-playing game',
  keyFeature1: 'Procedurally generated worlds',
  keyFeature2: 'Over 100 unique characters',
  keyFeature3: 'Cross-platform multiplayer',
  keyBenefits: 'endless replayability, nostalgic gameplay, and social gaming experience',
  testimonialQuote: 'Pixel Quest Adventures brings back all the magic of classic RPGs with modern twists!',
  callToAction: 'Pre-order now and get exclusive content!',
  website: 'www.crittersquest.com/pixelquest'
};

// Define the user inputs for an event teaser
const eventTeaser = {
  eventName: 'Pixel Con 2023',
  eventDate: 'December 15-17, 2023',
  eventLocation: 'GameHub Arena, Silicon Valley',
  attraction1: 'Exclusive game previews',
  attraction2: 'Meet & greet with developers',
  attraction3: 'Retro gaming tournaments',
  keyAttractions: 'gaming competitions, developer panels, and exclusive merchandise',
  callToAction: 'Register now - Early bird tickets available!',
  website: 'www.crittersquest.com/pixelcon'
};

// Choose which template to use
const templateType = process.argv[2] || 'product-announcement';
const artistName = process.argv[3]; // Optional artist name for artist-promo
const outputPath = process.argv[4] || `./output/${templateType}_${Date.now()}.mp4`;

// Determine which user inputs to use based on template type
let userInputs: Record<string, any>;

if (templateType === 'artist-promo') {
  if (!artistName) {
    console.error('Error: Artist name is required for artist-promo template');
    console.log('Usage: npm run artist "Artist Name"');
    process.exit(1);
  }
  userInputs = { artistName };
} else if (templateType.includes('product')) {
  userInputs = productAnnouncement;
} else if (templateType.includes('event')) {
  userInputs = eventTeaser;
} else {
  console.error(`Unknown template type: ${templateType}`);
  console.log('Available templates: product-announcement, event-teaser, artist-promo');
  process.exit(1);
}

// Create the branded video
createBrandedVideo(templateType, userInputs, outputPath)
  .then(() => {
    console.log('Video creation process completed.');
  })
  .catch(error => {
    console.error('Failed to create video:', error);
    process.exit(1);
  }); 