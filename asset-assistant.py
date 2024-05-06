import os
import PIL.Image
import platform
import requests
import shutil
import sys
import time
import yaml
from datetime import datetime
from modules.logs import MyLogger
from modules.notifications import discord, summary

logger = MyLogger()

## Start ##
start_time = time.time()
with open("VERSION", "r") as f:
    version = f.read().strip()
    logger.info(f"    Version: v{version}")
platform_info = platform.platform()
logger.info(f"    Platform: {platform.platform()}")
logger.separator(text="Asset Assistent Starting", debug=False)
  
## Load Config ##  
try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
        logger.info(" Loading config.yml...")
        logger.info(" Config loaded successfully")
        logger.separator(text="Config", space=False, border=False, debug=True)
except FileNotFoundError:
    logger.error(f" Config file 'config.yml' not found at {os.path.dirname(os.path.abspath(__file__))}. Terminating script.")
    sys.exit(1)

## Paths ##
process_dir = config['process']
movies_dir = config['movies']
shows_dir = config['shows']
collections_dir = config['collections']
script_dir = os.path.dirname(os.path.abspath(__file__))
failed_dir = os.path.join(script_dir, 'failed')
backup_enabled = config.get('enable_backup', False)
backup_dir = os.path.join(script_dir, 'backup')
naming_convention = config.get('naming_convention', None)

logger.debug(" Process directory:")
logger.debug(f" - {process_dir}")
logger.debug(f" Movies directory:")
logger.debug(f" - {movies_dir}")
logger.debug(f" TV Shows directory:")
logger.debug(f" - {shows_dir}")
logger.debug(f" Collections directory:")
logger.debug(f" - {collections_dir}")
logger.debug("")

## Naming convention ##
if naming_convention == None:
    logger.warn(" Naming convention:") 
    logger.debug("   Skipping:") 
    logger.debug("   - Collection assets")
    logger.debug("")
else:
    if naming_convention == "kodi" or naming_convention == "kometa":
        logger.debug(f" Naming convention: {naming_convention.capitalize()}")
        logger.debug("   Enabling:")
        logger.debug("   - Collection assets")
        logger.debug("")
    else:
        logger.debug(f" Naming convention: {naming_convention.capitalize()}")
        logger.debug("   Skipping:")
        logger.debug("   - Collection assets")
        logger.debug("")

## Failed Directory ##
if not os.path.exists(failed_dir):
    os.makedirs(failed_dir)
    logger.debug(" Failed directory not found...")
    logger.debug(" Successfully created failed directory")
    logger.debug("")
else:
    logger.debug(f" Failed Directory:")
    logger.debug(f" - {failed_dir}")
    logger.debug("")

## Backup Directory ##
if backup_enabled:
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.debug(f" Backup Enabled: {backup_enabled}")
        logger.debug(" Backup directory not found...")
        logger.debug(" Successfully created backup directory")
        logger.debug(f" Backup Directory:")
        logger.debug(f" - {backup_dir}")
    else:
        logger.debug(f" Backup Enabled: {backup_enabled}")
        logger.debug(f" Backup Directory:")
        logger.debug(f" - {backup_dir}")
else:
    logger.debug(f" Backup Enabled: {backup_enabled}")
    
logger.separator(text="Processing Images", debug=False, border=True)

## Match and copy Assets ##
def match_and_copy(filename, process_dir, shows_dir, movies_dir, collections_dir, failed_dir, copied_files):
    name, ext = os.path.splitext(filename)
    parts = name.split('(')
    if len(parts) >= 2:
        title = parts[0].strip()
        year = parts[1].split(')')[0].strip()
        for directory in [shows_dir, movies_dir]:
            for dir_name in os.listdir(directory):
                if f"{title} ({year})" in dir_name:
                    src = os.path.join(process_dir, filename)
                    dest = os.path.join(directory, dir_name, filename)
                    
                    shutil.copy(src, dest)
                    logger.info(f" Copied {filename} to directory: {dir_name}")
                    
                    with PIL.Image.open(dest) as img:
                        width, height = img.size
                        new_name = "poster" + ext if height > width else "background" + ext
                        new_dest = os.path.join(directory, dir_name, new_name)
                        os.rename(dest, new_dest)
                        logger.info(f" Renamed {filename} to {new_name}")
                        copied_files.append(new_dest)
                    
                    return directory
    else:
        if naming_convention == "kometa" or naming_convention == "kodi":
            for dir_name in os.listdir(collections_dir):
                if ("Collection" in name and name.replace("Collection", "").strip() in dir_name) or name in dir_name:
                    src = os.path.join(process_dir, filename)
                    dest = os.path.join(collections_dir, dir_name, filename)
                    
                    shutil.copy(src, dest)
                    logger.info(f" Copied {filename} to directory: {dir_name}")
                    
                    with PIL.Image.open(dest) as img:
                        width, height = img.size
                        new_name = "poster" + ext if height > width else "background" + ext
                        new_dest = os.path.join(collections_dir, dir_name, new_name)
                        os.rename(dest, new_dest)
                        logger.info(f' Renamed {filename} to {new_name}')
                        copied_files.append(new_dest)
                    
                    return collections_dir
        else:
            move_to_failed(filename, process_dir, failed_dir)
            logger.info(f" Failed to match {filename}")
            return failed_dir

    move_to_failed(filename, process_dir, failed_dir)
    return None
    
## Move failed assets ##
def move_to_failed(filename, process_dir, failed_dir):
    src = os.path.join(process_dir, filename)
    dest = os.path.join(failed_dir, filename)
    shutil.copy(src, dest)

copied_files = []

moved_counts = {'shows_dir': 0, 'movies_dir': 0, 'collections_dir': 0, 'failed_dir': 0}

directory_names = {
    shows_dir: 'shows_dir',
    movies_dir: 'movies_dir',
    collections_dir: 'collections_dir',
    failed_dir: 'failed_dir'
}
    
## Backup assets ##
for filename in os.listdir(process_dir):
    destination = match_and_copy(filename, process_dir, shows_dir, movies_dir, collections_dir, failed_dir, copied_files)
    if destination:
        if backup_enabled:
            src = os.path.join(process_dir, filename)
            shutil.move(src, os.path.join(backup_dir, filename))
            logger.info(f" Moved {filename} to backup directory")
            logger.info("")
        
        moved_counts[directory_names[destination]] += 1
    else:
        src = os.path.join(process_dir, filename)
        shutil.move(src, os.path.join(failed_dir, filename))
        moved_counts['failed_dir'] += 1
        logger.info(f" Failed to match {filename}. Moved to failed directory")
        logger.info("")

## End ##
end_time = time.time()
logger.separator(text="Summary", debug=False, border=True)

total_runtime = end_time - start_time
logger.info(f' Movie Assets: {moved_counts["movies_dir"]}')
logger.info(f' Show Assets: {moved_counts["shows_dir"]}')
logger.info(f' Collection Assets: {moved_counts["collections_dir"]}')
logger.info(f' Failures: {moved_counts["failed_dir"]}')

current_date = datetime.now()

## Notifications ##
summary = summary(moved_counts, backup_enabled, total_runtime, version)

## Discord notification ##
discord_webhook = config.get('discord_webhook')
if discord_webhook:
    discord(summary, discord_webhook, version, total_runtime)

## Version ##
version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file, 'r') as f:
    version = f.read().strip()

logger.separator(text=f'Asset Assistant Finished\nTotal runtime {total_runtime:2f} seconds', debug=False, border=True)
