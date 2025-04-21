const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const artists = require('../../assets/artists.json');

// Helper function to convert to sentence case
function toSentenceCase(str) {
  return str.toLowerCase().replace(/(^\w|\s\w)/g, letter => letter.toUpperCase());
}

// Function to get a random paper background
function getRandomPaperBackground() {
  const paperBgDir = path.join(__dirname, '..', '..', 'assets', 'paper_backgrounds');
  const files = fs.readdirSync(paperBgDir).filter(file => file.endsWith('.png'));
  const randomFile = files[Math.floor(Math.random() * files.length)];
  console.log(`Randomly selected paper background: ${randomFile}`);
  return path.join(paperBgDir, randomFile);
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
  
  // Replace paper background with random paper background
  const paperBgPath = getRandomPaperBackground();
  console.log('Using paper background path:', paperBgPath);
  template = template.replace(/PAPER_BACKGROUND_PATH/g, paperBgPath);
  
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
      <div class="mix-info">
        <p class="artist-display">${artistNameSentenceCase}</p>
        <p class="mix-display">${randomMix.mixTitle}</p>
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
    console.log('\nPreview image generated successfully!');
    console.log('Preview saved as: scene.png');
    console.log('\nYou can now make CSS changes to base_template.html and run this script again to see the updates.');
  } catch (error) {
    console.error('Error in render process:', error);
    process.exit(1);
  }
})(); 