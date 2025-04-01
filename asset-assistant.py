"""
Asset Assistant - A tool to organize and rename media assets.

This script processes images from a directory and copies them to
the appropriate location in a media library, renaming them according
to various media server conventions.
"""
import argparse
import os
import platform
import sys
import time
from datetime import datetime

from modules.logs import MyLogger
from modules.config_manager import ConfigManager
from modules.media_matcher import MediaMatcher
from modules.asset_processor import AssetProcessor
from modules.file_operations import unzip_files, process_directories, backup_file, delete_file, move_to_failed, compress_and_convert_images
from modules.notifications import discord, generate_summary

# Initialize logger with default settings (debug=False)
# The proper debug setting will be applied after loading config
logger = MyLogger()

def print_banner(version):
    """Print the Asset Assistant banner and version."""
    logger.separator()
    logger.info_center(r"     _                 _      _            _     _              _    ") 
    logger.info_center(r"    / \   ___ ___  ___| |_   / \   ___ ___(_)___| |_ __ _ _ __ | |_  ")
    logger.info_center(r"   / _ \ / __/ __|/ _ \ __| / _ \ / __/ __| / __| __/ _` | '_ \| __| ")
    logger.info_center(r" / ___ \\__ \__ \  __/ |_ / ___ \\__ \__ \ \__ \ || (_| | | | | |_  ")
    logger.info_center(r" /_/   \_\___/___/\___|\__/_/   \_\___/___/_|___/\__\__,_|_| |_|\__| ")
    logger.info("")
    logger.info("")
    logger.info(f" Version: v{version}")

def main():
    """Main function to run the Asset Assistant."""
    global logger
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Asset Assistant')
    parser.add_argument('--version', action='store_true', help='Print version and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    # Track execution time
    start_time = time.time()
    
    # Load version
    with open("VERSION", "r") as f:
        version = f.read().strip()

    # Handle version flag
    if args.version:
        print_banner(version)
        sys.exit(0)

    # Print banner and platform information
    print_banner(version)
    platform_info = platform.platform()
    logger.info(f" Platform: {platform.platform()}")
    logger.separator(text="Asset Assistant Starting", debug=False)

    # Load configuration
    config_manager = ConfigManager()
    if not config_manager.load_config():
        sys.exit(1)
    config = config_manager.config
    
    # Update logger with debug setting from config or command line
    debug_enabled = args.debug or config.get('debug', False)
    logger = MyLogger(debug=debug_enabled)
    if debug_enabled:
        logger.separator(text="Configuration Details", debug=True, border=True)
        logger.debug(f" PROCESSDIR: {config.get('process')}")
        logger.debug(f" SHOWSDIR: {config.get('shows')}")
        logger.debug(f" MOVIESDIR: {config.get('movies')}")
        logger.debug(f" COLLECTIONSDIR: {config.get('collections')}")
        logger.debug(f" FAILEDDIR: {config.get('failed')}")
        logger.debug(f" BACKUPDIR: {config.get('backup')}")
        logger.debug(f" LOGSDIR: {config.get('logs')}")
        logger.debug(f" ENABLE_BACKUP_SOURCE: {config.get('enable_backup_source', False)}")
        logger.debug(f" ENABLE_BACKUP_DESTINATION: {config.get('enable_backup_destination', False)}")
        logger.debug(f" SERVICE: {config.get('service', '')}")
        logger.debug(f" PLEX_SPECIALS: {config.get('plex_specials')}")
        logger.debug(f" COMPRESS_IMAGES: {config.get('compress_images', False)}")
        logger.debug(f" IMAGE_QUALITY: {config.get('image_quality', 85)}")
        logger.debug(f" DEBUG: {config.get('debug', False)}")

    # Get configuration variables
    process_dir = config['process']
    movies_dir = config['movies']
    shows_dir = config['shows']
    collections_dir = config['collections']
    failed_dir = config['failed']
    backup_dir = config['backup']
    backup_source = config.get('enable_backup_source', False)
    backup_destination = config.get('enable_backup_destination', False)
    service = config.get('service')
    compress_images = config.get('compress_images', False)
    image_quality = config.get('image_quality', 85)
    
    # Legacy support for the older 'enable_backup' setting
    if 'enable_backup' in config and not backup_source and not backup_destination:
        backup_source = config.get('enable_backup', False)
        backup_destination = config.get('enable_backup', False)
        logger.debug(" Using legacy 'enable_backup' setting for both source and destination backups")
    
    logger.separator(text="Processing Images", debug=False, border=True)

    # Extract zip files
    unzip_files(process_dir, failed_dir)

    # Process subdirectories
    process_directories(process_dir)
    
    # Compress images if enabled
    if compress_images:
        logger.info(" Image compression is enabled with the following settings:")
        logger.info(f" - Quality: {image_quality}")
        logger.info(f" - Process directory: {process_dir}")
        processed_count = compress_and_convert_images(process_dir, quality=image_quality)
        if processed_count > 0:
            logger.info(f" Processed {processed_count} images")
        else:
            logger.info(" No images were processed")

    # Setup media matcher and asset processor
    media_matcher = MediaMatcher(movies_dir, shows_dir, collections_dir)
    asset_processor = AssetProcessor(media_matcher, config)

    # Track processed files and counts
    moved_counts = {'movie': 0, 'show': 0, 'season': 0, 'episode': 0, 'collection': 0, 'failed': 0}
    
    # Create a list of supported file extensions
    standard_extensions = ('.jpg', '.jpeg', '.png')
    extended_extensions = ('.bmp', '.gif', '.tiff')
    
    # If compression is enabled, we can also process other image formats
    supported_extensions = standard_extensions + extended_extensions if compress_images else standard_extensions
    
    if compress_images and len(extended_extensions) > 0:
        logger.debug(f" Extended format support enabled: {', '.join(extended_extensions)}")

    # Get a stable snapshot of files before processing begins
    files_to_process = []
    for filename in os.listdir(process_dir):
        file_path = os.path.join(process_dir, filename)
        # Only include files (not directories) with supported extensions
        if os.path.isfile(file_path) and filename.lower().endswith(supported_extensions):
            files_to_process.append(filename)
        elif os.path.isfile(file_path):  # Handle non-image files
            if compress_images and filename.lower().endswith(extended_extensions):
                logger.info(f" Unsupported format without compression: {filename}")
            else:
                logger.info(f" Skipping non-image file: {filename}")
            move_to_failed(filename, process_dir, failed_dir)
            moved_counts['failed'] += 1

    logger.info(f" Found {len(files_to_process)} images to process")

    # Process all files in the stable snapshot
    for filename in files_to_process:
        # Skip if file disappeared during processing
        if not os.path.exists(os.path.join(process_dir, filename)):
            logger.warning(f" File disappeared during processing: {filename}")
            continue
            
        # Process the asset
        result_category = asset_processor.process_asset(filename)
        
        # Clean up the original file
        if result_category != 'failed':
            if backup_source:
                backup_file(filename, process_dir, backup_dir)
                logger.info(f" - Source file '{filename}' backed up")
            else:
                delete_file(os.path.join(process_dir, filename))
                
            logger.info("")
        
        # Update the counts
        moved_counts[result_category] += 1

    # Generate summary
    end_time = time.time()
    total_runtime = end_time - start_time
    logger.separator(text="Summary", debug=False, border=True)

    logger.info(f' Movie Assets: {moved_counts["movie"]}')
    logger.info(f' Show Assets: {moved_counts["show"]}')
    logger.info(f' Season Posters: {moved_counts["season"]}')
    logger.info(f' Episode Cards: {moved_counts["episode"]}')
    logger.info(f' Collection Assets: {moved_counts["collection"]}')
    logger.info(f' Failures: {moved_counts["failed"]}')

    # Generate summary for notifications
    summary = generate_summary(moved_counts, (backup_source, backup_destination), total_runtime, version)

    # Send Discord notification if configured
    discord_webhook = config.get('discord_webhook')
    if discord_webhook:
        discord(summary, discord_webhook, version, total_runtime)

    logger.separator(text=f'Asset Assistant Finished\nTotal runtime {total_runtime:.2f} seconds', debug=False, border=True)

if __name__ == "__main__":
    main()
