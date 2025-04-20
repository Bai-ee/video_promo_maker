import { generateTextOverlay } from '../lib/text-overlay';
import { loadBrandStyle } from '../lib/brand';

// Load brand style
const brandStyle = loadBrandStyle();

// Test dimensions (from README.md)
const width = 1160;
const height = 1456;

// Generate text overlays for AKILA
generateTextOverlay(
  'AKILA',
  'HOUSE MUSIC',
  width,
  height,
  brandStyle,
  './output/test/text_overlay_0.png',
  'heading'
);

generateTextOverlay(
  '...Head Ass!!!',
  '60min Live Set',
  width,
  height,
  brandStyle,
  './output/test/text_overlay_1.png',
  'heading'
);

generateTextOverlay(
  'Underground Existence',
  'New Mix Out Now',
  width,
  height,
  brandStyle,
  './output/test/text_overlay_2.png',
  'heading'
);

console.log('Text overlays generated in output/test/'); 