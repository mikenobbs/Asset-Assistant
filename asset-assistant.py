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
from modules.file_operations import unzip_files, process_directories, backup_file, delete_file, move_to_failed
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
        logger.info(" Debug logging enabled")

    # Get configuration variables
    process_dir = config['process']
    movies_dir = config['movies']
    shows_dir = config['shows']
    collections_dir = config['collections']
    failed_dir = config['failed']
    backup_dir = config['backup']
    backup_enabled = config.get('enable_backup', False)
    service = config.get('service')
    
    logger.separator(text="Processing Images", debug=False, border=True)

    # Extract zip files
    unzip_files(process_dir, failed_dir)

    # Process subdirectories
    process_directories(process_dir)

    # Setup media matcher and asset processor
    media_matcher = MediaMatcher(movies_dir, shows_dir, collections_dir)
    asset_processor = AssetProcessor(media_matcher, config)

    # Track processed files and counts
    moved_counts = {'movie': 0, 'show': 0, 'season': 0, 'episode': 0, 'collection': 0, 'failed': 0}
    
    # Create a list of supported file extensions
    supported_extensions = ('.jpg', '.jpeg', '.png')

    # Get a stable snapshot of files before processing begins
    files_to_process = []
    for filename in os.listdir(process_dir):
        file_path = os.path.join(process_dir, filename)
        # Only include files (not directories) with supported extensions
        if os.path.isfile(file_path) and filename.lower().endswith(supported_extensions):
            files_to_process.append(filename)
        elif os.path.isfile(file_path):  # Handle non-image files
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
            if backup_enabled:
                backup_file(filename, process_dir, backup_dir)
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
    summary = generate_summary(moved_counts, backup_enabled, total_runtime, version)

    # Send Discord notification if configured
    discord_webhook = config.get('discord_webhook')
    if discord_webhook:
        discord(summary, discord_webhook, version, total_runtime)

    logger.separator(text=f'Asset Assistant Finished\nTotal runtime {total_runtime:.2f} seconds', debug=False, border=True)

if __name__ == "__main__":
    main()
