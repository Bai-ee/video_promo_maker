const puppeteer = require('puppeteer');
const fs = require('fs');
const artists = require('../artists.json');
const path = require('path');

// Function to convert text to sentence case while preserving parenthetical content
function toSentenceCase(text) {
  // Split the text into main part and parenthetical part if it exists
  const matches = text.match(/(.*?)(\s*\(.*\))?$/);
  if (!matches) return text;

  const mainText = matches[1];
  const parenthetical = matches[2] || '';

  // Convert main text to sentence case
  const mainProcessed = mainText
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');

  // Convert parenthetical content to sentence case if it exists
  const parentheticalProcessed = parenthetical
    ? parenthetical.replace(/\((.*?)\)/g, match => {
        const inner = match.slice(1, -1);
        return '(' + inner.split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ') + ')';
      })
    : '';

  return mainProcessed + parentheticalProcessed;
}

// Function to update HTML template with artist data
function updateTemplate(artist) {
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
}

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Render CESAR RAMIREZ's scene
  updateTemplate(artists[5]);

  await page.goto('file://' + __dirname + '/updated_template.html');
  await page.setViewport({ width: 500, height: 600 });
  await page.screenshot({ path: 'scene.png' });

  await browser.close();
})();
