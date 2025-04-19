import fetch from 'node-fetch';

interface GPTResponse {
  choices?: Array<{
    message?: {
      content?: string;
    };
  }>;
  error?: any;
}

export async function generateScript(prompt: string): Promise<string> {
  console.log("Sending request to OpenAI API...");
  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4",
        messages: [
          { role: "system", content: "Create a short, engaging 1-minute script for a social media video." },
          { role: "user", content: prompt },
        ],
      }),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error("OpenAI API Error:", errorText);
      throw new Error(`OpenAI API returned ${res.status}: ${errorText}`);
    }

    const data = await res.json() as GPTResponse;
    
    if (data.error) {
      console.error("OpenAI API Error:", data.error);
      throw new Error(`OpenAI API Error: ${JSON.stringify(data.error)}`);
    }
    
    const content = data.choices?.[0]?.message?.content;
    if (!content) {
      console.error("No content returned from OpenAI:", data);
      return "This is a sample script for a video about AI in music production. AI is revolutionizing how music is created, produced, and distributed.";
    }
    
    console.log("Script content:", content);
    return content;
  } catch (error) {
    console.error("Error generating script:", error);
    // Return a fallback script
    return "This is a sample script for a video about AI in music production. AI is revolutionizing how music is created, produced, and distributed.";
  }
} 