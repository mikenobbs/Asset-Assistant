"""
Asset processor for Asset Assistant.
Handles processing and renaming of media assets.
"""
import os
import re
import PIL.Image
from modules.logs import MyLogger
from modules.file_operations import copy_file, rename_file, move_to_failed

logger = MyLogger()

class AssetProcessor:
    """Processes media assets and handles appropriate renaming."""
    
    def __init__(self, media_matcher, config):
        self.media_matcher = media_matcher
        self.config = config
        self.movies_dir = config.get('movies')
        self.shows_dir = config.get('shows')
        self.collections_dir = config.get('collections')
        self.process_dir = config.get('process')
        self.failed_dir = config.get('failed')
        self.service = config.get('service')
        self.plex_specials = config.get('plex_specials')
        
    def process_asset(self, filename):
        """Process a single asset file."""
        # Get file metadata from media matcher
        media_info = self.media_matcher.match_media(filename)
        
        category = media_info['category']
        season_number = media_info['season_number']
        episode_number = media_info['episode_number']
        
        if category not in ['movie', 'show', 'season', 'episode', 'collection']:
            self._handle_failed(filename, category)
            return 'failed'
        
        # Process based on category
        if category in ['movie', 'show']:
            return self._process_movie_or_show(filename, category)
        elif category == 'collection':
            return self._process_collection(filename)
        # Handle service-specific processing
        elif self.service == 'kometa':
            if category == 'season':
                return self._process_kometa_season(filename, season_number)
            elif category == 'episode':
                return self._process_kometa_episode(filename, season_number, episode_number)
        elif self.service == 'plex':
            if category == 'season':
                return self._process_plex_season(filename, season_number)
            elif category == 'episode':
                return self._process_plex_episode(filename, season_number, episode_number)
        elif self.service == 'kodi':
            # Implement kodi processing if needed
            pass
        
        # If we got here, something went wrong
        move_to_failed(filename, self.process_dir, self.failed_dir)
        return 'failed'
    
    def _handle_failed(self, filename, category):
        """Handle files that couldn't be categorized."""
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        if category == 'skip':
            logger.info(" - Asset skipped due to 'service' not being specified")
        elif category == 'not_supported':
            logger.info(f" - Asset skipped due to {self.service.capitalize()} not supporting collection assets")
        else:
            logger.info(" - Match not found, please double check file/directory naming")
        logger.info(" - Moved to failed directory")
        logger.info("")
    
    def _process_movie_or_show(self, filename, category):
        """Process movie or show poster."""
        directory = self.movies_dir if category == 'movie' else self.shows_dir
        if not directory:
            move_to_failed(filename, self.process_dir, self.failed_dir)
            return 'failed'
            
        # Instead of reimplementing matching logic, use the media_matcher's more robust matching
        if category == 'movie':
            # Extract name and year from filename
            name_year_match = re.match(r'(.+)\s\((\d{4})\)', filename, re.IGNORECASE)
            if name_year_match:
                file_name = name_year_match.group(1).strip()
                file_year = name_year_match.group(2)
                
                # Get all movie directories
                movie_dirs = os.listdir(directory)
                best_match = None
                
                # Try an exact match first
                exact_match = f"{file_name} ({file_year})"
                if exact_match in movie_dirs:
                    best_match = exact_match
                    logger.debug(f" Using exact match: '{exact_match}'")
                
                # If no exact match, try more flexible matching using the same variants as MediaMatcher
                if not best_match:
                    # Create variants of the file name to handle special characters
                    file_variants = [
                        file_name.lower(),
                        file_name.lower().replace("-", " "),
                        file_name.lower().replace(":", " "),
                        file_name.lower().replace("'", ""),
                        file_name.lower().replace(".", ""),
                        file_name.lower().replace("-", ""),
                        re.sub(r'[^\w\s]', '', file_name.lower()),
                        re.sub(r'[^\w\s]', ' ', file_name.lower())
                    ]
                    
                    for dir_name in movie_dirs:
                        dir_match = re.match(r'(.+)\s\((\d{4})\)', dir_name, re.IGNORECASE)
                        if dir_match:
                            dir_title = dir_match.group(1).strip()
                            dir_year = dir_match.group(2)
                            
                            # Skip if years don't match
                            if file_year != dir_year:
                                continue
                                
                            # Create variants of the directory name for better matching
                            dir_variants = [
                                dir_title.lower(),
                                dir_title.lower().replace("-", " "),
                                dir_title.lower().replace(":", " "),
                                dir_title.lower().replace("'", ""),
                                dir_title.lower().replace(".", ""),
                                dir_title.lower().replace("-", ""),
                                re.sub(r'[^\w\s]', '', dir_title.lower()),
                                re.sub(r'[^\w\s]', ' ', dir_title.lower())
                            ]
                            
                            # Check all variants against each other
                            for file_var in file_variants:
                                for dir_var in dir_variants:
                                    if (file_var == dir_var or 
                                        file_var in dir_var or 
                                        dir_var in file_var):
                                        best_match = dir_name
                                        logger.debug(f" Using flexible match: '{file_name}' -> '{dir_name}'")
                                        break
                                if best_match:
                                    break
                            if best_match:
                                break
            else:
                # Simple matching for files without year
                file_name_simple = filename.split('.')[0].lower()
                
                for dir_name in os.listdir(directory):
                    if file_name_simple == dir_name.lower().split('(')[0].strip():
                        best_match = dir_name
                        break
                
                # Last resort - partial match
                if not best_match:
                    for dir_name in os.listdir(directory):
                        if file_name_simple in dir_name.lower():
                            best_match = dir_name
                            logger.warning(f" - Using partial match: '{file_name_simple}' -> '{dir_name}'")
                            break
        else:
            # For show posters, use the same approach as before
            name_year_match = re.match(r'(.+)\s\((\d{4})\)', filename, re.IGNORECASE)
            
            best_match = None
            if name_year_match:
                file_name = name_year_match.group(1).strip().lower()
                file_year = name_year_match.group(2)
                
                for dir_name in os.listdir(directory):
                    dir_match = re.match(r'(.+)\s\((\d{4})\)', dir_name, re.IGNORECASE)
                    if dir_match:
                        dir_title = dir_match.group(1).strip().lower()
                        dir_year = dir_match.group(2)
                        
                        if file_name == dir_title and file_year == dir_year:
                            best_match = dir_name
                            break
                
                # Fall back to partial matching if needed
                if not best_match:
                    for dir_name in os.listdir(directory):
                        if file_name in dir_name.lower():
                            best_match = dir_name
                            logger.warning(f" - Using partial match: '{file_name}' -> '{dir_name}'")
                            break
            else:
                # Simple matching for files without year
                file_name_simple = filename.split('.')[0].lower()
                
                for dir_name in os.listdir(directory):
                    if file_name_simple == dir_name.lower().split('(')[0].strip():
                        best_match = dir_name
                        break
                
                # Last resort - partial match
                if not best_match:
                    for dir_name in os.listdir(directory):
                        if file_name_simple in dir_name.lower():
                            best_match = dir_name
                            logger.warning(f" - Using partial match: '{file_name_simple}' -> '{dir_name}'")
                            break
        
        # Process the matched directory
        if best_match:
            src = os.path.join(self.process_dir, filename)
            dest = os.path.join(directory, best_match, filename)
            
            if copy_file(src, dest, filename):
                # Determine new name based on aspect ratio
                try:
                    with PIL.Image.open(dest) as img:
                        width, height = img.size
                        if height > width:
                            new_name = "poster" + os.path.splitext(filename)[1]
                        else:
                            new_name = "fanart" + os.path.splitext(filename)[1]
                        
                        new_dest = os.path.join(directory, best_match, new_name)
                        rename_file(dest, new_dest)
                        
                        logger.info(f" {filename}:")
                        logger.info(f" - Category: {category.capitalize()}")
                        logger.info(f" - Copied to {best_match}")
                        logger.info(f" - Renamed to {new_name}")
                        return category
                        
                except Exception as e:
                    logger.error(f" - Error processing image: {e}")
                    return category
            
        # If we got here, no match was found
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: {category.capitalize()}")
        logger.error(" - No matching directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
    
    def _process_collection(self, filename):
        """Process collection asset."""
        # Check if we have appropriate service first
        if self.service not in ["kometa", "kodi"]:
            move_to_failed(filename, self.process_dir, self.failed_dir)
            logger.info(f" {filename}:")
            logger.info(f" - Category: Collection")
            logger.info(f" - Asset skipped due to {self.service.capitalize() if self.service else 'unspecified service'} not supporting collection assets")
            logger.info(" - Moved to failed directory")
            logger.info("")
            return 'failed'
            
        # Find matching collection directory - check BOTH collections_dir AND movies_dir
        matched = False
        file_base = filename.split('.')[0]
        
        # Create a list of directories to search, with their corresponding directory type
        search_dirs = []
        if self.collections_dir:
            search_dirs.append((self.collections_dir, "collections"))
        if self.movies_dir:
            search_dirs.append((self.movies_dir, "movies"))
            
        # If no valid directories to search, fail
        if not search_dirs:
            move_to_failed(filename, self.process_dir, self.failed_dir)
            return 'failed'
        
        # Search through all potential directories
        for directory, dir_type in search_dirs:
            for dir_name in os.listdir(directory):
                # Multiple comparison strategies
                file_name_norm = file_base.lower().replace("collection", "").strip()
                dir_name_norm = dir_name.lower().replace("collection", "").strip()
                
                file_name_clean = re.sub(r'[^\w\s]', '', file_name_norm)
                dir_name_clean = re.sub(r'[^\w\s]', '', dir_name_norm)
                
                # Add flexible matching with "collection" in the name for better detection
                dir_contains_collection = "collection" in dir_name.lower()
                file_contains_collection = "collection" in file_base.lower()
                
                if (file_name_norm == dir_name_norm or 
                    file_name_norm in dir_name_norm or 
                    dir_name_norm in file_name_norm or
                    file_name_clean == dir_name_clean or
                    (dir_contains_collection and file_name_clean in dir_name_clean) or
                    (file_contains_collection and dir_name_clean in file_name_clean)):
                    
                    src = os.path.join(self.process_dir, filename)
                    dest = os.path.join(directory, dir_name, filename)
                    
                    if copy_file(src, dest, filename):
                        # Determine new name based on aspect ratio
                        try:
                            with PIL.Image.open(dest) as img:
                                width, height = img.size
                                if height > width:
                                    new_name = "poster" + os.path.splitext(filename)[1]
                                else:
                                    new_name = "background" + os.path.splitext(filename)[1]
                                
                                new_dest = os.path.join(directory, dir_name, new_name)
                                rename_file(dest, new_dest)
                                
                                logger.info(f" {filename}:")
                                logger.info(f" - Category: Collection")
                                logger.info(f" - Copied to {dir_type}/{dir_name}")
                                logger.info(f" - Renamed to {new_name}")
                                matched = True
                                break
                        except Exception as e:
                            logger.error(f" - Error processing image: {e}")
            
            # If we found a match in this directory, no need to check others
            if matched:
                break
        
        if matched:
            return 'collection'
        
        # If no match was found in any directory
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: Collection")
        logger.error(f" - No matching collection directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
    
    def _process_kometa_season(self, filename, season_number):
        """Process season poster for Kometa."""
        if not self.shows_dir:
            return 'failed'
            
        # Find the show directory
        for dir_name in os.listdir(self.shows_dir):
            if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                src = os.path.join(self.process_dir, filename)
                dest = os.path.join(self.shows_dir, dir_name, filename)
                
                if copy_file(src, dest, filename):
                    # Determine new name
                    if season_number:
                        new_name = f"Season{season_number.zfill(2)}" + os.path.splitext(filename)[1]
                    else:
                        new_name = "Season00" + os.path.splitext(filename)[1]
                    
                    new_dest = os.path.join(self.shows_dir, dir_name, new_name)
                    rename_file(dest, new_dest)
                    
                    logger.info(f" {filename}:")
                    logger.info(f" - Category: Season")
                    logger.info(f" - Copied to {dir_name}")
                    logger.info(f" - Renamed to {new_name}")
                    return 'season'
        
        # If no match was found
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: Season")
        logger.error(f" - No matching show directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
    
    def _process_kometa_episode(self, filename, season_number, episode_number):
        """Process episode asset for Kometa."""
        if not self.shows_dir:
            return 'failed'
            
        # Find best show directory
        best_match = self.media_matcher.find_best_show_directory(filename)
        
        if best_match:
            src = os.path.join(self.process_dir, filename)
            dest = os.path.join(self.shows_dir, best_match, filename)
            
            if copy_file(src, dest, filename):
                new_name = f"S{season_number.zfill(2)}E{episode_number.zfill(2)}" + os.path.splitext(filename)[1]
                new_dest = os.path.join(self.shows_dir, best_match, new_name)
                rename_file(dest, new_dest)
                
                logger.info(f" {filename}:")
                logger.info(f" - Category: Episode")
                logger.info(f" - Copied to {best_match}")
                logger.info(f" - Renamed to {new_name}")
                return 'episode'
        
        # If no match was found
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: Episode")
        logger.error(f" - No matching show directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
    
    def _process_plex_season(self, filename, season_number):
        """Process season poster for Plex."""
        if not self.shows_dir:
            return 'failed'
            
        # Find the show directory
        show_dir = None
        matching_dir_name = None
        
        for dir_name in os.listdir(self.shows_dir):
            if filename.split(')')[0].strip().lower() in dir_name.split(')')[0].strip().lower():
                show_dir = os.path.join(self.shows_dir, dir_name)
                matching_dir_name = dir_name
                break
        
        if show_dir:
            # Determine season directory name
            if season_number:
                season_dir_name = f'Season {season_number.zfill(2)}'
            else:
                if 'Specials' in filename:
                    if self.plex_specials is None:
                        logger.error(" 'plex_specials' is not set in the config, please set it to True or False and try again")
                        return 'failed'
                    elif self.plex_specials:
                        season_dir_name = 'Specials'
                    else:
                        season_dir_name = 'Season 00'
            
            # Create the season directory if it doesn't exist
            season_dir = os.path.join(show_dir, season_dir_name)
            if not os.path.exists(season_dir):
                os.makedirs(season_dir)
                
            # Copy the file
            src = os.path.join(self.process_dir, filename)
            dest = os.path.join(season_dir, filename)
            
            if copy_file(src, dest, filename):
                # Rename the file
                if season_number:
                    new_name = f"Season{season_number.zfill(2)}" + os.path.splitext(filename)[1]
                else:
                    new_name = "season-specials-poster" + os.path.splitext(filename)[1]
                
                new_dest = os.path.join(season_dir, new_name)
                rename_file(dest, new_dest)
                
                logger.info(f" {filename}:")
                logger.info(f" - Category: Season")
                logger.info(f" - Copied to {matching_dir_name}/{season_dir_name}")
                logger.info(f" - Renamed to {new_name}")
                return 'season'
        
        # If no match was found
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: Season")
        logger.error(f" - No matching show directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
    
    def _process_plex_episode(self, filename, season_number, episode_number):
        """Process episode asset for Plex."""
        if not self.shows_dir:
            return 'failed'
            
        # Find best show directory  
        best_match = self.media_matcher.find_best_show_directory(filename)
        
        if best_match:
            show_dir = os.path.join(self.shows_dir, best_match)
            
            # Determine the season directory
            season_number = season_number.zfill(2)
            episode_number = episode_number.zfill(2)
            
            if season_number == '00':
                if self.plex_specials is None:
                    logger.error(" 'plex_specials' is not set in the config, please set it to True or False")
                    return 'failed'
                elif self.plex_specials:
                    season_dir_name = 'Specials'
                else:
                    season_dir_name = 'Season 00'
            else:
                season_dir_name = f'Season {season_number}'
            
            season_dir = os.path.join(show_dir, season_dir_name)
            if not os.path.exists(season_dir):
                move_to_failed(filename, self.process_dir, self.failed_dir)
                logger.info(f" {filename}:")
                logger.info(f" - Category: Episode")
                logger.error(f" - {season_dir_name} does not exist in {best_match}")
                logger.info(" - Moved to failed directory")
                logger.info("")
                return 'failed'
            
            # Find matching video file to use its name
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
                src = os.path.join(self.process_dir, filename)
                dest = os.path.join(season_dir, filename)
                new_dest = os.path.join(season_dir, episode_video_name)
                
                if copy_file(src, dest, filename) and rename_file(dest, new_dest):
                    logger.info(f" {filename}:")
                    logger.info(f" - Category: Episode")
                    logger.info(f" - Copied to {best_match}/{season_dir_name}")
                    logger.info(f" - Renamed to {episode_video_name}")
                    return 'episode'
            else:
                move_to_failed(filename, self.process_dir, self.failed_dir)
                logger.info(f" {filename}:")
                logger.info(f" - Category: Episode")
                logger.error(f" - Corresponding video file not found in {best_match}/{season_dir_name}")
                logger.info(" - Moved to failed directory")
                logger.info("")
                return 'failed'
        
        # If no match was found
        move_to_failed(filename, self.process_dir, self.failed_dir)
        logger.info(f" {filename}:")
        logger.info(f" - Category: Episode")
        logger.error(f" - No matching show directory found")
        logger.info(" - Moved to failed directory")
        logger.info("")
        return 'failed'
