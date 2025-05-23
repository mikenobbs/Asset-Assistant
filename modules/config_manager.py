"""
Configuration manager for Asset Assistant.
Handles loading and validating configuration from files and environment variables.
"""
import os
import yaml
from modules.logs import get_logger

# Get the singleton logger instance
logger = get_logger()

class ConfigManager:
    """Configuration manager for Asset Assistant."""
    
    def __init__(self):
        self.config = None
        self.config_paths = [
            '/config/config.yml',  # Docker volume mount path
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
                    
                    # Set default values for certain directories
                    self._set_default_paths()
                    
                    # Support for the split backup settings from the config file
                    # If only legacy 'enable_backup' is present, use it for both new settings
                    if 'enable_backup' in self.config and 'enable_backup_source' not in self.config:
                        self.config['enable_backup_source'] = self.config['enable_backup']
                    if 'enable_backup' in self.config and 'enable_backup_destination' not in self.config:
                        self.config['enable_backup_destination'] = self.config['enable_backup']
                    
                    break
            except FileNotFoundError:
                continue
        
        # If no config file was found, fall back to environment variables
        if not self.config:
            logger.warning(f" Config file not found. Tried: {', '.join(self.config_paths)}")
            logger.info(" Falling back to environment variables...")
            self.config = self._load_config_from_env()
            logger.info(" Configuration loaded from environment variables")
        else:
            # If config file was found, check for environment variables that should override
            self._override_with_env_vars()
            logger.info(" Applied environment variable overrides to configuration")
        
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
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'compress_images': os.getenv('COMPRESS_IMAGES', 'false').lower() == 'true',
            'image_quality': int(os.getenv('IMAGE_QUALITY', '85'))
        }
    
    def _set_default_paths(self):
        """Set default values for certain directories if they are not specified."""
        # Set default values for directories that should be in /config by default
        if 'backup' not in self.config or not self.config['backup']:
            self.config['backup'] = '/config/backup'
            
        if 'logs' not in self.config or not self.config['logs']:
            self.config['logs'] = '/config/logs'
            
        if 'process' not in self.config or not self.config['process']:
            self.config['process'] = '/config/process'
            
        if 'failed' not in self.config or not self.config['failed']:
            self.config['failed'] = '/config/failed'
            
    def _override_with_env_vars(self):
        """Override config file settings with environment variables if they exist."""
        # Path overrides
        if os.getenv('PROCESSDIR'):
            self.config['process'] = os.getenv('PROCESSDIR')
            logger.debug(f" - Overriding process directory with: {self.config['process']}")
            
        if os.getenv('SHOWSDIR'):
            self.config['shows'] = os.getenv('SHOWSDIR')
            logger.debug(f" - Overriding shows directory with: {self.config['shows']}")
            
        if os.getenv('MOVIESDIR'):
            self.config['movies'] = os.getenv('MOVIESDIR')
            logger.debug(f" - Overriding movies directory with: {self.config['movies']}")
            
        if os.getenv('COLLECTIONSDIR'):
            self.config['collections'] = os.getenv('COLLECTIONSDIR')
            logger.debug(f" - Overriding collections directory with: {self.config['collections']}")
            
        if os.getenv('FAILEDDIR'):
            self.config['failed'] = os.getenv('FAILEDDIR')
            logger.debug(f" - Overriding failed directory with: {self.config['failed']}")
            
        if os.getenv('BACKUPDIR'):
            self.config['backup'] = os.getenv('BACKUPDIR')
            logger.debug(f" - Overriding backup directory with: {self.config['backup']}")
            
        if os.getenv('LOGSDIR'):
            self.config['logs'] = os.getenv('LOGSDIR')
            logger.debug(f" - Overriding logs directory with: {self.config['logs']}")
            
        # Settings overrides
        if os.getenv('ENABLE_BACKUP_SOURCE'):
            self.config['enable_backup_source'] = os.getenv('ENABLE_BACKUP_SOURCE').lower() == 'true'
            logger.debug(f" - Overriding enable_backup_source with: {self.config['enable_backup_source']}")
            
        if os.getenv('ENABLE_BACKUP_DESTINATION'):
            self.config['enable_backup_destination'] = os.getenv('ENABLE_BACKUP_DESTINATION').lower() == 'true'
            logger.debug(f" - Overriding enable_backup_destination with: {self.config['enable_backup_destination']}")
            
        if os.getenv('SERVICE'):
            self.config['service'] = os.getenv('SERVICE')
            logger.debug(f" - Overriding service with: {self.config['service']}")
            
        if os.getenv('PLEX_SPECIALS'):
            self.config['plex_specials'] = os.getenv('PLEX_SPECIALS').lower() == 'true'
            logger.debug(f" - Overriding plex_specials with: {self.config['plex_specials']}")
            
        if os.getenv('DISCORD_WEBHOOK'):
            self.config['discord_webhook'] = os.getenv('DISCORD_WEBHOOK')
            logger.debug(" - Overriding discord_webhook")
            
        if os.getenv('DEBUG'):
            self.config['debug'] = os.getenv('DEBUG').lower() == 'true'
            logger.debug(f" - Overriding debug with: {self.config['debug']}")
            
        if os.getenv('COMPRESS_IMAGES'):
            self.config['compress_images'] = os.getenv('COMPRESS_IMAGES').lower() == 'true'
            logger.debug(f" - Overriding compress_images with: {self.config['compress_images']}")
            
        if os.getenv('IMAGE_QUALITY'):
            self.config['image_quality'] = int(os.getenv('IMAGE_QUALITY'))
            logger.debug(f" - Overriding image_quality with: {self.config['image_quality']}")
    
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
