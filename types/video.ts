export interface VideoElement {
  type: string;
  content?: string;
  style?: string;
  position?: string;
  animation?: string;
  color?: string;
  prompt?: string;
}

export interface VideoSection {
  type: string;
  duration: number;
  elements: VideoElement[];
}

export interface VideoTemplate {
  templateName: string;
  templateType: string;
  scriptTemplate: string;
  sections: VideoSection[];
  audioOptions: {
    duration: number;
    fadeIn: number;
    fadeOut: number;
  };
} 