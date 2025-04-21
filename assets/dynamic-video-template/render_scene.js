const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const artists = require('../../assets/artists.json');
const { AudioProcessor } = require('../../dist/lib/audio-processor');

// Helper function to convert to sentence case
function toSentenceCase(str) {
  return str.toLowerCase().replace(/(^\w|\s\w)/g, letter => letter.toUpperCase());
}

// Function to get a random artist from the artists array
function getRandomArtist() {
  const randomIndex = Math.floor(Math.random() * artists.length);
  const artist = artists[randomIndex];
  console.log(`Randomly selected artist: ${artist.artistName} (index: ${randomIndex})`);
  return artist;
}

// Function to update HTML template with artist data
async function updateTemplate(artist) {
  console.log('Copying base_template.html to updated_template.html');
  // Copy the entire base template content
  let template = fs.readFileSync(__dirname + '/base_template.html', 'utf8');
  console.log('Original Template:', template);

  // Convert artist name to sentence case and replace
  const artistNameSentenceCase = toSentenceCase(artist.artistName);
  template = template.replace(/BAI-EE/g, artistNameSentenceCase);
  const imagePath = artist.artistImageFilename.replace('img/artists/', '');
  const fullImagePath = `${__dirname}/../../assets/artist_thumbnails/${imagePath}`;
  console.log('Using image path:', fullImagePath);
  template = template.replace(/path\/to\/your\/image\.jpg/g, fullImagePath);
  
  // Replace background image with absolute path
  const bgImagePath = `${__dirname}/../../assets/backgrounds/generic_bg.jpg`;
  console.log('Using background image path:', bgImagePath);
  template = template.replace(/assets\/backgrounds\/generic_bg\.jpg/g, bgImagePath);
  
  // Replace logo image with absolute path
  const logoPath = path.join(__dirname, '..', '..', 'assets', 'logos', 'ue_logo_horiz.png');
  console.log('Using logo path:', logoPath);
  template = template.replace(/assets\/logos\/ue_logo_horiz\.png/g, logoPath);
  
  // Replace genre
  template = template.replace(/GENRE_PLACEHOLDER/g, artist.artistGenre);
  
  // Generate mix HTML for one random mix
  const randomMix = artist.mixes[Math.floor(Math.random() * artist.mixes.length)];
  const mixesHtml = `
    <div class="mix">
      <h3>${randomMix.mixTitle}</h3>
      <div class="mix-info">
        <p>Duration: ${randomMix.mixDuration}</p>
        <p>Date: ${randomMix.mixDateYear}</p>
      </div>
      <a href="${randomMix.mixArweaveURL}" target="_blank"></a>
    </div>
  `;
  
  // Replace mixes placeholder
  template = template.replace(/<!-- MIXES_PLACEHOLDER -->/g, mixesHtml);
  
  // Ensure dimensions are not altered
  template = template.replace(/width: \d+px;/, 'width: 500px;');
  template = template.replace(/height: \d+px;/, 'height: 600px;');
  
  console.log('Updated Template with artist info:', template);
  // Write the updated template to updated_template.html
  fs.writeFileSync(__dirname + '/updated_template.html', template);
  console.log('Updated template written to updated_template.html');

  // Process audio from the random mix
  console.log('Processing audio from mix URL:', randomMix.mixArweaveURL);
  try {
    const audioResult = await AudioProcessor.processAudioUrl(
      randomMix.mixArweaveURL,
      30, // 30 second clip
      2,  // 2 second fade in
      2   // 2 second fade out
    );
    console.log('Audio processing result:', audioResult);
    
    // Move the processed audio to temp_audio.mp3
    fs.copyFileSync(audioResult.clipPath, path.join(__dirname, 'temp_audio.mp3'));
    console.log('Audio clip saved as temp_audio.mp3');
    
    // Clean up the original clip
    await AudioProcessor.cleanupClip(audioResult.clipPath);
    console.log('Original audio clip cleaned up');
  } catch (error) {
    console.error('Error processing audio:', error);
    console.log('Continuing without audio...');
  }
}

(async () => {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Get and render a random artist's scene
    const randomArtist = getRandomArtist();
    await updateTemplate(randomArtist);

    await page.goto('file://' + __dirname + '/updated_template.html');
    await page.setViewport({ width: 500, height: 600 });
    await page.screenshot({ path: 'scene.png' });

    await browser.close();
  } catch (error) {
    console.error('Error in render process:', error);
    process.exit(1);
  }
})();
