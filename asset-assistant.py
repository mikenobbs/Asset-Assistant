import os
import PIL.Image
import platform
import requests
import shutil
import sys
import time
import yaml
import re
from datetime import datetime
from modules.logs import MyLogger
from modules.notifications import discord, generate_summary

logger = MyLogger()


## start ##
start_time = time.time()
with open("VERSION", "r") as f:
    version = f.read().strip()
    logger.separator()
    logger.info_center("     _                 _      _            _     _              _    ") 
    logger.info_center("    / \   ___ ___  ___| |_   / \   ___ ___(_)___| |_ __ _ _ __ | |_  ")
    logger.info_center("   / _ \ / __/ __|/ _ \ __| / _ \ / __/ __| / __| __/ _` | '_ \| __| ")
    logger.info_center(r" / ___ \\__ \__ \  __/ |_ / ___ \\__ \__ \ \__ \ || (_| | | | | |_  ")
    logger.info_center(" /_/   \_\___/___/\___|\__/_/   \_\___/___/_|___/\__\__,_|_| |_|\__| ")
    logger.info("")
    logger.info("")
    logger.info(f" Version: v{version}")
platform_info = platform.platform()
logger.info(f" Platform: {platform.platform()}")
logger.separator(text="Asset Assistant Starting", debug=False)


## load config ##  
try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
        logger.info(" Loading config.yml...")
        logger.info(" Config loaded successfully")
        logger.separator(text="Config", space=False, border=False, debug=True)
except FileNotFoundError:
    logger.error(f" Config file 'config.yml' not found at {os.path.dirname(os.path.abspath(__file__))}. Terminating script.")
    sys.exit(1)


## paths ##
process_dir = config['process']
movies_dir = config['movies']
shows_dir = config['shows']
collections_dir = config['collections']
script_dir = os.path.dirname(os.path.abspath(__file__))
failed_dir = os.path.join(script_dir, 'failed')
backup_enabled = config.get('enable_backup', False)
backup_dir = os.path.join(script_dir, 'backup')
service = config.get('service', None)
plex_specials = config.get('plex_specials', None)


## path check ##
unique_paths = {process_dir, movies_dir, shows_dir, collections_dir}
if len(unique_paths) != 4:
    logger.error(" Directory paths must be unique. Terminating script.")
    sys.exit(1)
  
    
## check process directory ##
if not os.path.exists(process_dir):
    logger.error(f" Process directory '{process_dir}' not found. Terminating script.")
    sys.exit(1)


## check media directories ##
optional_dirs = {
    'movies': movies_dir,
    'shows': shows_dir,
    'collections': collections_dir
}

for dir_name, dir_path in optional_dirs.items():
    if dir_path and not os.path.exists(dir_path):
        optional_dirs[dir_name] = None
        
logger.debug(" Process directory:")
logger.debug(f" - {process_dir}")
logger.debug(f" Movies directory:")
if movies_dir:
    logger.debug(f" - {movies_dir}")
else:
    logger.warning(f" - Directory not found. Skipping movies.")
logger.debug(f" Shows directory:")
if shows_dir:
    logger.debug(f" - {shows_dir}")
else:
    logger.warning(f" - Directory not found, skipping shows")
logger.debug(f" Collections directory:")
if collections_dir:
    logger.debug(f" - {collections_dir}")
else:
    logger.warning(f" - Directory not found, skipping collections")
logger.debug("")


## service check ##
if service == None:
    logger.warning(" Naming convention: Not set") 
    logger.debug("   Skipping:") 
    logger.debug("   - Season posters")
    logger.debug("   - Episode cards")
    logger.debug("   - Collection assets")
    logger.debug("")
else:
    if service == "kodi" or service == "kometa":
        logger.debug(f" Naming convention: {service.capitalize()}")
        logger.debug("   Enabling:")
        logger.debug("   - Season posters")
        logger.debug("   - Episode cards")
        logger.debug("   - Collection assets")
        logger.debug("")
    else:
        logger.debug(f" Naming convention: {service.capitalize()}")
        logger.debug("   Enabling:")
        logger.debug("   - Season posters")
        logger.debug("   - Episode cards")
        logger.debug("   Skipping:")
        logger.debug("   - Collection assets")
        logger.debug("")

## failed directory ##
if not os.path.exists(failed_dir):
    os.makedirs(failed_dir)
    logger.debug(" Failed directory not found...")
    logger.debug(" Successfully created failed directory")
    logger.debug(f" - {failed_dir}")
    logger.debug("")
else:
    logger.debug(f" Failed Directory:")
    logger.debug(f" - {failed_dir}")
    logger.debug("")

## backup directory ##
if backup_enabled:
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.debug(f" Backup Enabled: {backup_enabled}")
        logger.debug(" Backup directory not found...")
        logger.debug(" Successfully created backup directory")
        logger.debug(f" - {backup_dir}")
    else:
        logger.debug(f" Backup Enabled: {backup_enabled}")
        logger.debug(f" Backup Directory:")
        logger.debug(f" - {backup_dir}")
else:
    logger.debug(f" Backup Enabled: {backup_enabled}")
    
logger.separator(text="Processing Images", debug=False, border=True)

## define categories ##
def categories(filename, movies_dir, shows_dir):
    season_pattern = re.compile(r'Season\s+(\d+)', re.IGNORECASE)
    episode_pattern = re.compile(r'S(\d+)[\s\.]?E(\d+)', re.IGNORECASE)
    specials_pattern = re.compile(r'Specials', re.IGNORECASE)

    season_match = season_pattern.search(filename)
    episode_match = episode_pattern.search(filename)
    specials_match = specials_pattern.search(filename)
    
    category = None
    season_number = None 
    episode_number = None

    if season_match:
        if service:
            category = 'season'
            season_number = season_match.group(1)
        else:
            category = 'skip'
    elif specials_match:
        if service:
            category = 'season'
        else:
            category = 'skip'
    elif episode_match:
        if service:
            category = 'episode'
            season_number = episode_match.group(1)
            episode_number = episode_match.group(2)
        else:
            category = 'skip'
    else:
        for dir_name in os.listdir(collections_dir):
            if filename.split('.')[0].lower().replace("collection", "").strip() == dir_name.lower().replace("collection", "").strip():
                if (service in ["kometa", "kodi"]):
                    category = 'collection'
                    break
                elif service not in ["kometa", "kodi"]:
                    category = 'skip'
                break
        else:
            for dir_name in os.listdir(movies_dir):
                if filename.split('.')[0].lower() in dir_name.lower():
                    category = 'movie'
                    break
            else:
                for dir_name in os.listdir(shows_dir):
                    if filename.split('.')[0].lower() in dir_name.lower():
                        category = 'show'
                        break

    if category not in ['movie', 'show', 'season', 'episode', 'collection']:
        move_to_failed(filename, process_dir, failed_dir)
        logger.info(f" {filename}:")
        if category == 'skip':
            logger.info(" - Asset skipped due to chosen naming convention")
        elif movies_dir == None:
            logger.info(" - Skipped due to missing movies directory")
        elif shows_dir == None:
            logger.info(" - Skipped due to missing shows directory")
        elif collections_dir == None:
            logger.info(" - Skipped due to missing collections directory")
        else:
            logger.info(" - Match not found, please double check file/directory naming")
        logger.info(" - Moved to failed directory")
        logger.info("")

    return category, season_number, episode_number
    
# copy and rename #
def copy_and_rename(filename, category, season_number, episode_number, movies_dir, shows_dir, collections_dir, process_dir, failed_dir, service):
    category, season_number, episode_number = categories(filename, movies_dir, shows_dir)
    src = os.path.join(process_dir, filename)
    dest = None
    new_dest = None
    directory = None

    if category == 'movie' or category == 'show':
        directory = movies_dir if category == 'movie' else shows_dir
        for dir_name in os.listdir(directory):
            if filename.split('.')[0].lower() in dir_name.lower():
                dest = os.path.join(directory, dir_name, filename)
                shutil.copy(src, dest)
                logger.info(f" {filename}:")
                logger.info(f" - Category: {category.capitalize()}")
                logger.info(f" - Copied to {dir_name}")
                with PIL.Image.open(dest) as img:
                    width, height = img.size
                    new_name = "poster" + os.path.splitext(filename)[1] if height > width else "background" + os.path.splitext(filename)[1]
                    new_dest = os.path.join(directory, dir_name, new_name)
                    os.rename(dest, new_dest)
                    logger.info(f" - Renamed {new_name}")
                return category
                    
   #elif service == 'emby' 
   
   #elif service == 'jellyfin'
   
   #elif service == 'kodi'
    
    elif service == 'kometa':
        if category == 'season':
            directory = shows_dir
            for dir_name in os.listdir(directory):
                if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                    dest = os.path.join(directory, dir_name, filename)
                    shutil.copy(src, dest)
                    logger.info(f" {filename}:")
                    logger.info(f" - Category: {category.capitalize()}")
                    logger.info(f" - Copied to {dir_name}")
                    if season_number:
                        new_name = f"Season{season_number.zfill(2)}" + os.path.splitext(filename)[1]
                    else:
                        new_name = "Season00" + os.path.splitext(filename)[1]
                    new_dest = os.path.join(directory, dir_name, new_name)
                    os.rename(dest, new_dest)
                    logger.info(f" - Renamed {new_name}")
                    return category

        elif category == 'episode':
            directory = shows_dir
            for dir_name in os.listdir(directory):
                if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                    dest = os.path.join(directory, dir_name, filename)
                    shutil.copy(src, dest)
                    logger.info(f" {filename}:")
                    logger.info(f" - Category: {category.capitalize()}")
                    logger.info(f" - Copied to {dir_name}")
                    new_name = f"S{season_number.zfill(2)}E{episode_number.zfill(2)}" + os.path.splitext(filename)[1]
                    new_dest = os.path.join(directory, dir_name, new_name)
                    os.rename(dest, new_dest)
                    logger.info(f" - Renamed {new_name}")
                    return category
                    
    elif service == 'plex':
        if category == 'season':
            directory = shows_dir
            for dir_name in os.listdir(directory):
                if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                    show_dir = os.path.join(directory, dir_name)
                if season_number:
                    season_dir_name = f'Season {season_number.zfill(2)}'
                else:
                    if 'Specials' in filename:
                        if plex_specials is None:
                            logger.error(" 'plex_specials' is not set in the config, please set it to True or False and try again")
                            sys.exit(1)
                        elif plex_specials:
                            season_dir_name = 'Specials'
                        else:
                            season_dir_name = 'Season 00'
                season_dir = os.path.join(show_dir, season_dir_name)
                if not os.path.exists(season_dir):
                    os.makedirs(season_dir)
                dest = os.path.join(season_dir, filename)
                shutil.copy(src, dest)
                logger.info(f" {filename}:")
                logger.info(f" - Category: {category.capitalize()}")
                logger.info(f" - Copied to {dir_name}/{season_dir_name}")
                if season_number:
                    new_name = f"Season{season_number.zfill(2)}" + os.path.splitext(filename)[1]
                else:
                    new_name = "season-specials-poster" + os.path.splitext(filename)[1] 
                new_dest = os.path.join(season_dir, new_name)
                os.rename(dest, new_dest)
                logger.info(f" - Renamed {new_name}")
                return category
                
        elif category == 'episode':
            directory = shows_dir
            for dir_name in os.listdir(directory):
                if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                    show_dir = os.path.join(directory, dir_name)
                    
                    episode_match = re.match(r'.*S(\d+)[\s\.]?E(\d+)', filename, re.IGNORECASE)
                    if episode_match:
                        season_number = episode_match.group(1)
                        episode_number = episode_match.group(2)
                    else:
                        move_to_failed(filename, process_dir, failed_dir)
                        category = 'failed'
                        logger.info(f" {filename}:")
                        logger.info(f" - Category: {category.capitalize()}")
                        logger.error(" - Failed to extract season and episode numbers")
                        logger.info(" - Moved to failed directory")
                        logger.info("")
                        return category
                    season_number = season_number.zfill(2)
                    episode_number = episode_number.zfill(2)
                    if season_number == '00':
                        if plex_specials is None:
                            logger.error(" 'plex_specials' is not set in the config, please set it to True or False and try again")
                            sys.exit(1)
                        elif plex_specials:
                            season_dir_name = 'Specials'
                        else:
                            season_dir_name = 'Season 00'
                    else:
                        season_dir_name = f'Season {season_number.zfill(2)}'
                    season_dir = os.path.join(show_dir, season_dir_name)
                    if not os.path.exists(season_dir):
                        move_to_failed(filename, process_dir, failed_dir)                       
                        category = 'failed'
                        logger.info(f" {filename}:")
                        logger.info(f" - Category: {category.capitalize()}")
                        logger.error(f" - {season_dir_name} does not exist in {dir_name}")
                        logger.info(" - Moved to failed directory")
                        logger.info("")
                        return category
                    episode_video_name = None
                    for video_file in os.listdir(season_dir):
                        if video_file.endswith(('.mkv', '.mp4', '.avi')):
                            video_match = re.match(r'.*S(\d+)[\s\.]?E(\d+)', video_file, re.IGNORECASE)
                            if video_match:
                                video_season_number = video_match.group(1)
                                video_episode_number = video_match.group(2)
                                if season_number == video_season_number and episode_number == video_episode_number:
                                    episode_video_name = os.path.splitext(video_file)[0] + os.path.splitext(filename)[1]
                                    break
                    if episode_video_name:
                        new_name = episode_video_name
                        new_dest = os.path.join(season_dir, new_name)
                        dest = os.path.join(season_dir, filename)
                        shutil.copy(src, dest)
                        os.rename(dest, new_dest)
                        logger.info(f" {filename}:")
                        logger.info(f" - Category: {category.capitalize()}")
                        logger.info(f" - Copied to {dir_name}/{season_dir_name}")
                        logger.info(f" - Renamed {new_name}")
                        return category
                    else:
                        move_to_failed(filename, process_dir, failed_dir)
                        category = 'failed'
                        logger.info(f" {filename}:")
                        logger.info(f" - Category: {category.capitalize()}")
                        logger.error(f" - Corresponding video file not found in {dir_name}/{season_dir_name}")
                        logger.info(" - Moved to failed directory")
                        logger.info("")
                        return category
            return category

    elif category == 'collection':
        directory = collections_dir
        for dir_name in os.listdir(directory):
            if filename.split('.')[0].lower().replace("collection", "").strip() in dir_name.lower():
                dest = os.path.join(directory, dir_name, filename)
                shutil.copy(src, dest)
                logger.info(f" {filename}:")
                logger.info(f" - Category: {category.capitalize()}")
                logger.info(f" - Copied to {dir_name}")
                with PIL.Image.open(dest) as img:
                    width, height = img.size
                    new_name = "poster" + os.path.splitext(filename)[1] if height > width else "background" + os.path.splitext(filename)[1]
                    new_dest = os.path.join(directory, dir_name, new_name)
                    os.rename(dest, new_dest)
                    logger.info(f" - Renamed {new_name}")
                    return category
    else:
        move_to_failed(filename, process_dir, failed_dir)
    
    return category

## move failed assets ##
def move_to_failed(filename, process_dir, failed_dir):
    src = os.path.join(process_dir, filename)
    dest = os.path.join(failed_dir, filename)
    moved_counts['failed'] += 1
    
    try:
        shutil.move(src, dest)
    except FileNotFoundError:
        logger.error(" - File not found during move to failed directory")
    except PermissionError:
        logger.error(" - Permission denied when movingto failed directory")
    except Exception as e:
        logger.error(f" - Failed to move to failed directory: {e}")

## backup assets ##
def backup(filename, process_dir, backup_dir):
    src = os.path.join(process_dir, filename)
    dest = os.path.join(backup_dir, filename)
    
    try:
        shutil.move(src, dest)
        logger.info(" - Moved to backup directory")
    except FileNotFoundError:
        logger.error(" - File not found during backup")
    except PermissionError:
        logger.error(" - Permission denied when backing up")
    except Exception as e:
        logger.error(" - Failed to backup to backup directory: {e}")
    
copied_files = []

moved_counts = {'movie':0, 'show': 0, 'season': 0, 'episode': 0, 'collection': 0, 'failed': 0}
    

## processing loop ##           
for filename in os.listdir(process_dir):
    category, season_number, episode_number = categories(filename, movies_dir, shows_dir)
    if category in ['movie', 'show', 'season', 'episode', 'collection']:
        updated_category = copy_and_rename(filename, category, season_number, episode_number, movies_dir, shows_dir, collections_dir, process_dir, failed_dir, service)
        if updated_category != 'failed':
            if backup_enabled:
                backup(filename, process_dir, backup_dir)
                logger.info("")
            else:
                try:
                    os.remove(os.path.join(process_dir, filename))
                    logger.info(" - Deleted from process directory")
                except FileNotFoundError:
                    logger.error(" - File not found during deletion")
                except PermissionError:
                    logger.error(" - Permission denied when deleting")
                except Exception as e:
                    logger.error(f" - Failed to delete: {e}")
            logger.info("")
            moved_counts[updated_category] += 1

## end ##
end_time = time.time()
logger.separator(text="Summary", debug=False, border=True)

total_runtime = end_time - start_time
logger.info(f' Movie Assets: {moved_counts["movie"]}')
logger.info(f' Show Assets: {moved_counts["show"]}')
logger.info(f' Season Posters: {moved_counts["season"]}')
logger.info(f' Episode Cards: {moved_counts["episode"]}')
logger.info(f' Collection Assets: {moved_counts["collection"]}')
logger.info(f' Failures: {moved_counts["failed"]}')

current_date = datetime.now()

## notifications ##
summary = generate_summary(moved_counts, backup_enabled, total_runtime, version)

## discord notification ##
discord_webhook = config.get('discord_webhook')
if discord_webhook:
    discord(summary, discord_webhook, version, total_runtime)

## version ##
version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file, 'r') as f:
    version = f.read().strip()

logger.separator(text=f'Asset Assistant Finished\nTotal runtime {total_runtime:2f} seconds', debug=False, border=True)
