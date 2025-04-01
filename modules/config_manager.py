"""
Configuration manager for Asset Assistant.
Handles loading and validating configuration from files and environment variables.
"""
import os
import yaml
from modules.logs import MyLogger

logger = MyLogger()

class ConfigManager:
    """Configuration manager for Asset Assistant."""
    
    def __init__(self):
        self.config = None
        self.config_paths = [
            os.path.join('config', 'config.yml'),  # /config/config.yml
            'config.yml'  # ./config.yml
        ]
    
    def load_config(self):
        """Load configuration from files or environment variables."""
        # Try to load from config files first
        for config_path in self.config_paths:
            try:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                    logger.info(f" Configuration loaded from {config_path}")
                    
                    # Support for the split backup settings from the config file
                    # If only legacy 'enable_backup' is present, use it for both new settings
                    if 'enable_backup' in self.config and 'enable_backup_source' not in self.config:
                        self.config['enable_backup_source'] = self.config['enable_backup']
                    if 'enable_backup' in self.config and 'enable_backup_destination' not in self.config:
                        self.config['enable_backup_destination'] = self.config['enable_backup']
                    
                    break
            except FileNotFoundError:
                continue
        
        # Fall back to environment variables
        if not self.config:
            logger.warning(f" Config file not found. Tried: {', '.join(self.config_paths)}")
            logger.info(" Falling back to environment variables...")
            self.config = self._load_config_from_env()
            logger.info(" Configuration loaded from environment variables")
        
        # Validate configuration
        if not self.config:
            logger.error(" No configuration found in files or environment")
            logger.error(f" Current directory: {os.getcwd()}")
            return False
            
        return self._validate_config()
    
    def _load_config_from_env(self):
        """Load configuration from environment variables with defaults."""
        return {
            'process': os.getenv('PROCESSDIR', '/config/process'),
            'shows': os.getenv('SHOWSDIR', '/config/shows'),
            'movies': os.getenv('MOVIESDIR', '/config/movies'),
            'collections': os.getenv('COLLECTIONSDIR', '/config/collections'),
            'failed': os.getenv('FAILEDDIR', '/config/failed'),
            'backup': os.getenv('BACKUPDIR', '/config/backup'),
            'logs': os.getenv('LOGSDIR', '/config/logs'),
            'enable_backup_source': os.getenv('ENABLE_BACKUP_SOURCE', 'false').lower() == 'true',
            'enable_backup_destination': os.getenv('ENABLE_BACKUP_DESTINATION', 'false').lower() == 'true',
            'enable_backup': os.getenv('ENABLE_BACKUP', 'false').lower() == 'true',  # Legacy support
            'service': os.getenv('SERVICE', ''),
            'plex_specials': None if os.getenv('PLEX_SPECIALS', '') == '' else os.getenv('PLEX_SPECIALS', '').lower() == 'true',
            'discord_webhook': os.getenv('DISCORD_WEBHOOK', ''),
            'discord_enabled': os.getenv('DISCORD_ENABLED', 'false').lower() == 'true',
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'compress_images': os.getenv('COMPRESS_IMAGES', 'false').lower() == 'true',
            'image_quality': int(os.getenv('IMAGE_QUALITY', '85'))
        }
    
    def _validate_config(self):
        """Validate the configuration."""
        # Check for required directories
        process_dir = self.config.get('process')
        movies_dir = self.config.get('movies')
        shows_dir = self.config.get('shows')
        collections_dir = self.config.get('collections')
        
        # Path uniqueness check
        unique_paths = {process_dir, movies_dir, shows_dir, collections_dir}
        if len(unique_paths) != len([p for p in unique_paths if p]):  # Only count non-None paths
            logger.error(" Directory paths must be unique. Terminating script.")
            return False
            
        # Check process directory
        if not process_dir or not os.path.exists(process_dir):
            logger.error(f" Process directory '{process_dir}' not found. Terminating script.")
            return False
            
        # Check other directories
        optional_dirs = {
            'movies': movies_dir,
            'shows': shows_dir,
            'collections': collections_dir
        }

        for dir_name, dir_path in optional_dirs.items():
            if dir_path and not os.path.exists(dir_path):
                logger.warning(f" {dir_name.capitalize()} directory '{dir_path}' not found. Skipping {dir_name}.")
                self.config[dir_name] = None
        
        # Create failed directory if it doesn't exist
        failed_dir = self.config.get('failed')
        if failed_dir and not os.path.exists(failed_dir):
            os.makedirs(failed_dir)
            logger.debug(" Failed directory not found...")
            logger.debug(" Successfully created failed directory")
            logger.debug(f" - {failed_dir}")
        
        # Create backup directory if needed and enabled
        backup_enabled = self.config.get('enable_backup', False)
        backup_dir = self.config.get('backup')
        if backup_enabled and backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            logger.debug(f" Backup Enabled: {backup_enabled}")
            logger.debug(" Backup directory not found...")
            logger.debug(" Successfully created backup directory")
            logger.debug(f" - {backup_dir}")
            
        # Log configuration
        self._log_config()
        return True
    
    def _log_config(self):
        """Log the current configuration."""
        # Print full configuration when debug is enabled
        if self.config.get('debug', False):
            logger.debug(" === FULL CONFIGURATION DUMP ===")
            for key, value in sorted(self.config.items()):
                logger.debug(f" {key}: {value}")
            logger.debug(" === END CONFIGURATION DUMP ===")
        
        logger.debug(" Process directory:")
        logger.debug(f" - {self.config.get('process')}")
        
        logger.debug(" Movies directory:")
        if self.config.get('movies'):
            logger.debug(f" - {self.config.get('movies')}")
        else:
            logger.warning(" - Directory not found. Skipping movies.")
            
        logger.debug(" Shows directory:")
        if self.config.get('shows'):
            logger.debug(f" - {self.config.get('shows')}")
        else:
            logger.warning(" - Directory not found, skipping shows")
            
        logger.debug(" Collections directory:")
        if self.config.get('collections'):
            logger.debug(f" - {self.config.get('collections')}")
        else:
            logger.warning(" - Directory not found, skipping collections")
            
        service = self.config.get('service')
        if not service:
            logger.warning(" Naming convention: Not set") 
            logger.debug("   Skipping:") 
            logger.debug("   - Season posters")
            logger.debug("   - Episode cards")
            logger.debug("   - Collection assets")
        elif service == "kodi" or service == "kometa":
            logger.debug(f" Naming convention: {service.capitalize()}")
            logger.debug("   Enabling:")
            logger.debug("   - Season posters")
            logger.debug("   - Episode cards")
            logger.debug("   - Collection assets")
        else:
            logger.debug(f" Naming convention: {service.capitalize()}")
            logger.debug("   Enabling:")
            logger.debug("   - Season posters")
            logger.debug("   - Episode cards")
            logger.debug("   Skipping:")
            logger.debug("   - Collection assets")
            
        logger.debug(f" Failed Directory:")
        logger.debug(f" - {self.config.get('failed')}")
        
        backup_enabled = self.config.get('enable_backup', False)
        logger.debug(f" Backup Enabled: {backup_enabled}")
        if backup_enabled:
            logger.debug(f" Backup Directory:")
            logger.debug(f" - {self.config.get('backup')}")
