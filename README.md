# Video Promo Maker

A tool for creating promotional videos for artists using AI-generated content and templates.

## Features

- Generates 30-second promotional videos
- Supports multiple artists from a JSON database
- Includes audio clip integration
- AI-generated imagery and scripts
- Customizable templates
- Video dimensions: 1160x1456

## Requirements

- Node.js
- FFmpeg
- OpenAI API key

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key_here
```

3. Add artist data to `assets/artists.json`

## Usage

To create a video for an artist:
```bash
npm run artist "Artist Name"
```

## Templates

Available templates in `templates/` directory:
- artist-promo.json
- product-demo.json
- tutorial-video.json
- brand-video.json
- product-announcement.json
- event-teaser.json 