#!/usr/bin/env python3
"""
🔐 Self-Managing API Key System
Automatically handles API key configuration, validation, and rotation
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
import json
from datetime import datetime
import logging

class APIKeyManager:
    """Self-managing API key system that handles configuration automatically"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.env_file = self.project_root / ".env"
        self.config_file = self.project_root / ".api_config.json"
        self.backup_file = self.project_root / ".env.backup"
        
        # Load actual keys from environment or existing .env file
        self.primary_keys = self._load_actual_keys()
        
        # Backup/Rotation keys for quota exhaustion scenarios
        self.backup_keys = {
            "WEBCRAWLER_API_KEY": [
                "webcrawler-backup-key-1",  # Add your backup keys here
                "webcrawler-backup-key-2",  # Add your backup keys here
                # Add more backup keys here as needed
            ]
        }
        
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for API key operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - API_KEY_MANAGER - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / 'api_key_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_env_file_exists(self) -> bool:
        """Ensure .env file exists with current working API keys"""
        try:
            if not self.env_file.exists():
                self.logger.info("🔧 Creating .env file with primary API keys...")
                self.create_env_file()
                return True
            
            # Verify existing .env file has all required keys
            existing_keys = self.load_env_file()
            missing_keys = []
            
            for key, value in self.primary_keys.items():
                if key not in existing_keys or not existing_keys[key]:
                    missing_keys.append(key)
            
            if missing_keys:
                self.logger.warning(f"⚠️ Missing API keys in .env: {missing_keys}")
                self.update_env_file()
                return True
            
            self.logger.info("✅ .env file exists with all required keys")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error ensuring .env file: {e}")
            return False
    
    def create_env_file(self):
        """Create .env file with primary API keys"""
        env_content = []
        for key, value in self.primary_keys.items():
            env_content.append(f"{key}={value}")
        
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_content) + '\n')
        
        self.logger.info(f"✅ Created .env file at {self.env_file}")
    
    def load_env_file(self) -> Dict[str, str]:
        """Load existing .env file and return key-value pairs"""
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        return env_vars
    
    def update_env_file(self):
        """Update .env file with current primary keys"""
        # Backup existing file
        if self.env_file.exists():
            import shutil
            shutil.copy(self.env_file, self.backup_file)
            self.logger.info(f"📦 Backed up existing .env to {self.backup_file}")
        
        # Create new .env with primary keys
        self.create_env_file()
    
    def rotate_api_key(self, key_name: str) -> bool:
        """Rotate to backup API key when quota is exhausted"""
        if key_name not in self.backup_keys:
            self.logger.warning(f"⚠️ No backup keys available for {key_name}")
            return False
        
        backup_list = self.backup_keys[key_name]
        current_key = self.primary_keys[key_name]
        
        # Find next available backup key
        for backup_key in backup_list:
            if backup_key != current_key:
                self.logger.info(f"🔄 Rotating {key_name} to backup key: {backup_key[:10]}...")
                self.primary_keys[key_name] = backup_key
                self.update_env_file()
                return True
        
        self.logger.error(f"❌ No available backup keys for {key_name}")
        return False
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate all API keys are properly formatted"""
        validation_results = {}
        
        for key, value in self.primary_keys.items():
            if key == "OPENAI_API_KEY":
                validation_results[key] = value.startswith("sk-")
            elif key == "GOOGLE_API_KEY":
                validation_results[key] = value.startswith("AIzaSy") and len(value) == 39
            elif key == "WEBCRAWLER_API_KEY":
                validation_results[key] = len(value) >= 16 and value.replace("-", "").isalnum()
            else:
                validation_results[key] = bool(value)
        
        return validation_results
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables for subprocess execution"""
        env_vars = os.environ.copy()
        
        # Override with current primary keys
        for key, value in self.primary_keys.items():
            env_vars[key] = value
        
        return env_vars
    
    def check_and_fix_quota_exhaustion(self, error_message: str) -> bool:
        """Automatically handle quota exhaustion by rotating keys"""
        if "Payment Required" in error_message or "Insufficient credits" in error_message:
            self.logger.warning("💳 Quota exhaustion detected - attempting key rotation...")
            
            if "webcrawler" in error_message.lower() or "402" in error_message:
                return self.rotate_api_key("WEBCRAWLER_API_KEY")
            
        return False
    
    def generate_config_report(self) -> str:
        """Generate a comprehensive configuration report"""
        validation = self.validate_api_keys()
        env_exists = self.env_file.exists()
        
        report = f"""
🔐 API Key Manager Configuration Report
{'='*50}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 Project Root: {self.project_root}
📄 .env File: {'✅ Exists' if env_exists else '❌ Missing'}

🔑 API Key Validation:
"""
        
        for key, is_valid in validation.items():
            status = "✅ Valid" if is_valid else "❌ Invalid"
            masked_key = self.primary_keys[key][:10] + "..." if self.primary_keys.get(key) else "Missing"
            report += f"  {key}: {status} ({masked_key})\n"
        
        report += f"""
📦 Backup Keys Available:
"""
        for key, backups in self.backup_keys.items():
            report += f"  {key}: {len(backups)} backup keys available\n"
        
        return report

    def auto_setup(self) -> bool:
        """Automatically set up the entire API key system"""
        self.logger.info("🚀 Starting automatic API key setup...")
        
        try:
            # 1. Ensure .env file exists
            if not self.ensure_env_file_exists():
                return False
            
            # 2. Validate all keys
            validation = self.validate_api_keys()
            invalid_keys = [k for k, v in validation.items() if not v]
            
            if invalid_keys:
                self.logger.error(f"❌ Invalid API keys detected: {invalid_keys}")
                return False
            
            # 3. Test environment loading
            env_vars = self.get_environment_variables()
            for key in self.primary_keys.keys():
                if key not in env_vars:
                    self.logger.error(f"❌ {key} not found in environment variables")
                    return False
            
            self.logger.info("✅ API key system setup completed successfully!")
            print(self.generate_config_report())
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Auto-setup failed: {e}")
            return False

    def _load_actual_keys(self) -> Dict[str, str]:
        """Load actual API keys from environment or existing .env file"""
        # Try to load from existing .env file first
        if self.env_file.exists():
            env_keys = self.load_env_file()
            if all(key in env_keys and env_keys[key] for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY", "WEBCRAWLER_API_KEY"]):
                return {
                    "OPENAI_API_KEY": env_keys["OPENAI_API_KEY"],
                    "GOOGLE_API_KEY": env_keys["GOOGLE_API_KEY"],
                    "WEBCRAWLER_API_KEY": env_keys["WEBCRAWLER_API_KEY"]
                }
        
        # Try to load from environment variables
        env_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "WEBCRAWLER_API_KEY": os.getenv("WEBCRAWLER_API_KEY")
        }
        
        if all(env_keys.values()):
            return env_keys
        
        # Fallback to placeholder values (user needs to configure)
        return {
            "OPENAI_API_KEY": "your-openai-key-here",
            "GOOGLE_API_KEY": "your-google-key-here",
            "WEBCRAWLER_API_KEY": "b0a58413f6d2d8acb2bd"  # Provided WebcrawlerAPI key
        }

def main():
    """Command-line interface for API key manager"""
    manager = APIKeyManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            success = manager.auto_setup()
            sys.exit(0 if success else 1)
        elif command == "report":
            print(manager.generate_config_report())
        elif command == "rotate" and len(sys.argv) > 2:
            key_name = sys.argv[2].upper()
            success = manager.rotate_api_key(key_name)
            sys.exit(0 if success else 1)
        else:
            print("Usage: python api_key_manager.py [setup|report|rotate KEY_NAME]")
    else:
        # Default: auto-setup
        manager.auto_setup()

if __name__ == "__main__":
    main() 