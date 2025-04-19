export interface Mix {
  title: string;
  duration: number;
  mixArweaveURL: string;
}

export interface Artist {
  name: string;
  genre: string;
  mixes: Mix[];
}

export async function loadArtists(): Promise<Artist[]> {
  // TODO: Replace with actual data loading from a database or API
  return [
    {
      name: "BLUE JAY (AKA Josh Zeitler)",
      genre: "Electronic",
      mixes: [
        {
          title: "Blue Jay Mix 001",
          duration: 3600, // 60 minutes
          mixArweaveURL: "https://arweave.net/example-mix-1"
        }
      ]
    },
    {
      name: "Chicago Skyway",
      genre: "House",
      mixes: [
        {
          title: "Chicago Skyway for Hakeem",
          duration: 5400, // 90 minutes
          mixArweaveURL: "https://arweave.net/example-mix-2"
        }
      ]
    }
  ];
} 