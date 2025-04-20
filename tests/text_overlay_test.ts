import { generateTextOverlay } from '../lib/text-overlay';
import { ensureDirExists } from '../lib/utils';
import { loadBrandStyle } from '../lib/brand';

const outputDir = './output/scenes';
ensureDirExists(outputDir);

const brandStyle = loadBrandStyle();

const artistData = {
  name: 'AKILA',
  genre: 'house',
  mixTitle: '...Head Ass!!!',
  mixDuration: '60:00'
};

// Generate text overlays
generateTextOverlay(
  artistData.name,
  artistData.genre.toUpperCase() + ' MUSIC',
  1160,
  1456,
  brandStyle,
  `${outputDir}/text_overlay_0.png`
);
console.log('Generated text_overlay_0.png');

generateTextOverlay(
  artistData.mixTitle,
  `${artistData.mixDuration} Live Set`,
  1160,
  1456,
  brandStyle,
  `${outputDir}/text_overlay_1.png`
);
console.log('Generated text_overlay_1.png');

generateTextOverlay(
  'Underground Existence',
  'New Mix Out Now',
  1160,
  1456,
  brandStyle,
  `${outputDir}/text_overlay_2.png`
);
console.log('Generated text_overlay_2.png'); 