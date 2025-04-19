import { Artist, Mix } from '../artists';
import { BrandStyle } from '../brand';
import { VideoTemplate, VideoSection } from '../types';
import { renderTextToImage } from './html-renderer';
import { composeVideo } from './video-composer';
import { generateAudioClip } from '../audio-processor';
import path from 'path';
import fs from 'fs';

export interface VideoRenderOptions {
  artist: Artist;
  mix: Mix;
  template: VideoTemplate;
  brandStyle: BrandStyle;
  outputPath: string;
}

export async function createArtistVideo(options: VideoRenderOptions): Promise<string> {
  const { artist, mix, template, brandStyle, outputPath } = options;

  // Generate audio clip
  console.log('Generating audio clip...');
  const audioClipPath = await generateAudioClip(mix.mixArweaveURL, 30, 2963);

  // Create temporary directory for rendered frames
  const tempDir = path.join(process.cwd(), 'output', 'temp', Date.now().toString());
  await fs.promises.mkdir(tempDir, { recursive: true });

  try {
    // Render each section using HTML templates
    console.log('Rendering video sections...');
    const renderedImages: string[] = [];
    
    for (let i = 0; i < template.sections.length; i++) {
      const section = template.sections[i];
      const templatePath = path.join(process.cwd(), 'templates', 'html', `${section.type || 'intro'}-slide.html`);
      
      const imagePath = path.join(tempDir, `section_${i}.png`);
      await renderTextToImage({
        template: templatePath,
        data: {
          artistName: artist.name,
          genre: artist.genre,
          mixTitle: mix.title,
          mixDuration: `${Math.floor(mix.duration / 60)} min`,
          ...section.data
        },
        outputPath: imagePath,
        width: 1160,
        height: 1456,
        animationDuration: 1000,
        brandStyle
      });
      
      renderedImages.push(imagePath);
    }

    // Compose final video
    console.log('Composing final video...');
    const finalVideo = await composeVideo({
      images: renderedImages,
      audio: audioClipPath,
      outputPath,
      duration: 30, // 30 seconds total
      width: 1160,
      height: 1456,
      fps: 30
    });

    return finalVideo;
  } finally {
    // Clean up temporary files
    try {
      await fs.promises.rm(tempDir, { recursive: true, force: true });
      await fs.promises.unlink(audioClipPath);
    } catch (error) {
      console.warn('Error cleaning up temporary files:', error);
    }
  }
} 