import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { config } from 'dotenv';

// Load environment variables
config();

interface ChatResponse {
  choices?: Array<{
    message?: {
      content?: string;
    };
  }>;
}

async function testImageGeneration() {
  // Load our style guide
  const styleGuide = JSON.parse(fs.readFileSync('./config/thumbnail_style_guide.json', 'utf8'));
  const basePrompt = styleGuide.thumbnailStyleGuide.aiPrompt;
  
  console.log('🎨 Testing GPT-4o Image Generation');
  console.log('----------------------------------');
  
  try {
    // First attempt: Direct image generation request
    console.log('\n📝 Test 1: Direct image generation request');
    const response1 = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant capable of generating images. When asked to create an image, generate it directly - no explanations needed."
          },
          {
            role: "user",
            content: `Generate an image: ${basePrompt} Make it a portrait of a musician in an underground studio.`
          }
        ],
        max_tokens: 1000
      })
    });

    const data1 = await response1.json() as ChatResponse;
    console.log('\nResponse 1:');
    console.log(data1.choices?.[0]?.message?.content);

    // Second attempt: Ask for image URL format
    console.log('\n📝 Test 2: Requesting specific URL format');
    const response2 = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant that generates images. Please respond ONLY with a markdown image link in the format: ![description](image_url)"
          },
          {
            role: "user",
            content: `Create this image and return ONLY the markdown image link: ${basePrompt} Make it a portrait of a musician in an underground studio.`
          }
        ],
        max_tokens: 1000
      })
    });

    const data2 = await response2.json() as ChatResponse;
    console.log('\nResponse 2:');
    console.log(data2.choices?.[0]?.message?.content);

    // Third attempt: Multi-turn conversation
    console.log('\n📝 Test 3: Multi-turn conversation about image generation');
    const response3 = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant that can generate images."
          },
          {
            role: "user",
            content: "I need you to generate an image. Can you do that directly or do you need to use DALL-E?"
          },
          {
            role: "assistant",
            content: "I can help generate images. Please provide the description of what you'd like to create."
          },
          {
            role: "user",
            content: `Generate this image: ${basePrompt} Make it a portrait of a musician in an underground studio.`
          }
        ],
        max_tokens: 1000
      })
    });

    const data3 = await response3.json() as ChatResponse;
    console.log('\nResponse 3:');
    console.log(data3.choices?.[0]?.message?.content);

  } catch (error) {
    console.error('❌ Error during testing:', error);
  }
}

// Run the test
console.log('🚀 Starting image generation tests...\n');
testImageGeneration().then(() => {
  console.log('\n✅ Tests completed');
}).catch(error => {
  console.error('❌ Test suite failed:', error);
}); 