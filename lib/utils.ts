import { existsSync, mkdirSync } from 'fs';

/**
 * Ensures a directory exists, creating it recursively if it doesn't
 * @param dirPath The directory path to ensure exists
 */
export function ensureDirExists(dirPath: string): void {
  if (!existsSync(dirPath)) {
    mkdirSync(dirPath, { recursive: true });
  }
} 