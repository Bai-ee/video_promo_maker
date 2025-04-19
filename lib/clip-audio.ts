import { AudioProcessor } from './audio-processor';

async function main() {
  const url = process.argv[2];
  const duration = process.argv[3] ? parseInt(process.argv[3], 10) : 30;

  if (!url) {
    console.error('Error: No URL provided.');
    console.error('Usage: npm run clip <audio-url> [duration-in-seconds]');
    process.exit(1);
  }

  try {
    console.log('Processing audio...');
    const result = await AudioProcessor.processAudioUrl(url, duration);
    
    console.log('\nAudio clip created successfully:');
    console.log(`Path: ${result.clipPath}`);
    console.log(`Duration: ${result.duration} seconds`);
    console.log(`Start Time: ${result.startTime} seconds`);
    
    // Keep the clip file for now - it will be cleaned up when used in video generation
    console.log('\nNote: The clip file will be automatically cleaned up after video generation.');
    
  } catch (error) {
    console.error('Failed to process audio:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main(); 