export interface VideoSection {
  imagePath?: string;
  duration: number;
  text?: string;
  style?: {
    fontFamily?: string;
    fontSize?: number;
    color?: string;
    backgroundColor?: string;
  };
}

export interface VideoTemplate {
  name: string;
  description: string;
  scriptTemplate: string;
  sections: VideoSection[];
  duration: number;
} 