"""
Media matching module for Asset Assistant.
Contains functions for matching media files with appropriate directories.
"""
import os
import re
from modules.logs import get_logger

class MediaMatcher:
    def __init__(self, movies_dir=None, shows_dir=None, collections_dir=None, debug=None):
        self.movies_dir = movies_dir
        self.shows_dir = shows_dir
        self.collections_dir = collections_dir
        
        # Store debug setting
        self.debug = debug
        
        # Store logger instance to avoid repeated get_logger calls
        self.logger = get_logger(debug=debug)
        
        # Cache for directory listings to improve performance
        self._dir_cache = {}
        
    def match_media(self, filename):
        """Determine the category of a media file and extract relevant information."""
        # Define patterns
        season_pattern = re.compile(r'(?:^|\s|-)\s*Season\s+(\d+)', re.IGNORECASE)
        episode_pattern = re.compile(r'S(\d+)[\s\.]?E(\d+)', re.IGNORECASE)
        specials_pattern = re.compile(r'Specials', re.IGNORECASE)
        media_pattern = re.compile(r'(.+)\s\((\d{4})\)', re.IGNORECASE)
        collection_pattern = re.compile(r'(.+?)(?:\s+Collection|\s*collection)(?:\s*\.|\s*$)', re.IGNORECASE)

        # Match patterns against filename
        season_match = season_pattern.search(filename)
        episode_match = episode_pattern.search(filename)
        specials_match = specials_pattern.search(filename)
        media_match = media_pattern.search(filename)
        collection_match = collection_pattern.search(filename)
        
        # Initialize variables
        category = None
        season_number = None 
        episode_number = None
        show_name = None
        show_year = None

        self.logger.info(f" {filename}:")
        
        # Extract media name and year if available
        if media_match:
            show_name = media_match.group(1).strip()
            show_year = media_match.group(2).strip()
            self.logger.debug(f" - Extracted media name: '{show_name}', year: '{show_year}'")
        
        # Check if it's a movie
        if media_match and self.movies_dir:
            movie_found = self._find_movie_match(show_name, show_year)
            if movie_found:
                category = 'movie'
        
        # Check if it's a collection
        if category is None and collection_match and self.collections_dir:
            collection_name = collection_match.group(1).strip()
            self.logger.debug(f" - Detected possible collection: '{collection_name}'")
            
            if self._find_collection_match(filename, collection_name):
                category = 'collection'
        
        # Check for TV show categories
        if category is None and self.shows_dir:
            # Check for season
            if season_match:
                category = 'season'
                season_number = season_match.group(1)
                if show_name and not self._find_show_directory(show_name, show_year):
                    category = None
                    
            # Check for specials
            elif specials_match:
                category = 'season'
                season_number = None  # Explicitly set to None for specials
                if show_name and not self._find_show_directory(show_name, show_year):
                    category = None
                    
            # Check for episode
            elif episode_match:
                category = 'episode'
                season_number = episode_match.group(1)
                episode_number = episode_match.group(2)
                self.logger.debug(f" - Found episode S{season_number}E{episode_number}")
                
                if show_name and not self._find_show_directory(show_name, show_year):
                    category = None
            
            # Check for main show poster (filename is just show name and year)
            elif media_match and not season_match and not episode_match and not specials_match:
                # If the file has show name and year but no season/episode identifiers, 
                # and matches a show directory, it's the main show poster
                show_dir = self._find_show_directory(show_name, show_year)
                if show_dir:
                    category = 'show'
                    self.logger.debug(f" - Detected main show poster for '{show_name} ({show_year})'")
        
        return {
            'category': category,
            'season_number': season_number,
            'episode_number': episode_number,
            'show_name': show_name,
            'show_year': show_year
        }

    def _get_dir_listing(self, directory):
        """Get directory listing with caching for performance."""
        if directory not in self._dir_cache:
            try:
                self._dir_cache[directory] = os.listdir(directory)
            except (FileNotFoundError, PermissionError):
                self._dir_cache[directory] = []
        return self._dir_cache[directory]
    
    def _create_name_variants(self, name):
        """Create different variants of a name for matching."""
        if not name:
            return []
            
        name_lower = name.lower()
        variants = [
            name_lower,
            name_lower.replace("-", " "),
            name_lower.replace(":", " "),
            name_lower.replace("'", ""),
            name_lower.replace(".", ""),
            name_lower.replace("-", ""),
            re.sub(r'[^\w\s]', '', name_lower),
            re.sub(r'[^\w\s]', ' ', name_lower),
            re.sub(r'\s+', '', name_lower.replace("-", "")),  # Normalized version
            # Handle colon replacements with dashes (with various spacing)
            # Colons are often replaced as: ":" -> "-", " -", "- ", or " - "
            re.sub(r'-\s+', ' - ', name_lower),  # "word- word" -> "word - word"
            re.sub(r'\s+-', ' - ', name_lower),  # "word -word" -> "word - word"
            re.sub(r'-', ' - ', name_lower),     # "word-word" -> "word - word"
            re.sub(r'\s*-\s*', ' ', name_lower), # Remove dashes entirely with spaces
        ]
        
        # Normalize multiple spaces and deduplicate
        normalized_variants = []
        for variant in variants:
            normalized = re.sub(r'\s+', ' ', variant).strip()
            if normalized not in normalized_variants:
                normalized_variants.append(normalized)
        
        return normalized_variants
        
    def _find_movie_match(self, movie_name, movie_year):
        """Find matching movie directory."""
        if not self.movies_dir or not movie_name:
            return False
            
        movie_variants = self._create_name_variants(movie_name)
        
        for dir_name in self._get_dir_listing(self.movies_dir):
            dir_match = re.match(r'(.+)\s\((\d{4})\)', dir_name, re.IGNORECASE)
            if dir_match:
                dir_name_clean = dir_match.group(1).strip()
                dir_year = dir_match.group(2)
                
                # Skip if years don't match
                if movie_year != dir_year:
                    continue
                    
                dir_variants = self._create_name_variants(dir_name_clean)
                
                # Check all variants against each other
                for movie_var in movie_variants:
                    for dir_var in dir_variants:
                        if (movie_var == dir_var or 
                            movie_var in dir_var or 
                            dir_var in movie_var):
                            self.logger.debug(f" - Found match: '{dir_name}")
                            return True
                            
                # Try normalized versions as a fallback
                movie_normalized = re.sub(r'\s+', '', movie_name.lower().replace("-", ""))
                dir_normalized = re.sub(r'\s+', '', dir_name_clean.lower().replace("-", ""))
                if movie_normalized == dir_normalized:
                    self.logger.debug(f" - Found match using normalized names: '{dir_name}")
                    return True
                    
        return False
        
    def _find_collection_match(self, filename, collection_name=None):
        """Find matching collection directory."""
        if not self.collections_dir:
            return False
            
        # Strip any extra spaces in the filename for better matching
        clean_filename = re.sub(r'\s+', ' ', filename.strip())
        file_base = os.path.splitext(clean_filename)[0].lower()
        
        # First try to find directories with "collection" in the name
        for dir_name in self._get_dir_listing(self.collections_dir):
            dir_base = dir_name.lower()
            
            # Strategy 1: Direct comparison after removing "Collection"
            file_name_norm = file_base.replace("collection", "").strip()
            dir_name_norm = dir_base.replace("collection", "").strip()
            
            # Strategy 2: Remove all special characters for comparison
            file_name_clean = re.sub(r'[^\w\s]', '', file_name_norm)
            dir_name_clean = re.sub(r'[^\w\s]', '', dir_name_norm)
            
            # Check if this is a potential match
            if (file_name_norm == dir_name_norm or 
                file_name_norm in dir_name_norm or 
                dir_name_norm in file_name_norm or
                file_name_clean == dir_name_clean):
                self.logger.debug(f" - Found collection match: '{dir_name}' for '{filename}'")
                return True
                
        return False
        
    def _find_show_directory(self, show_name, show_year):
        """Find matching TV show directory."""
        if not self.shows_dir or not show_name:
            return None
            
        expected_dir = f"{show_name} ({show_year})" if show_year else show_name
        self.logger.debug(f" - Looking for directory: {expected_dir}")
        
        # First try exact match
        if expected_dir and os.path.exists(os.path.join(self.shows_dir, expected_dir)):
            return expected_dir
            
        # Try less exact matches
        show_variants = self._create_name_variants(show_name)
        
        # First look for exact name matches with correct year
        for dir_name in self._get_dir_listing(self.shows_dir):
            dir_match = re.match(r'(.+)\s\((\d{4})\)', dir_name, re.IGNORECASE)
            if dir_match:
                dir_show_name = dir_match.group(1).strip()
                dir_show_year = dir_match.group(2)
                
                if show_year == dir_show_year:
                    # Use variants for better matching
                    dir_variants = self._create_name_variants(dir_show_name)
                    for show_var in show_variants:
                        if show_var in dir_variants:
                            return dir_name
        
        # Then try less exact matching
        matching_dirs = []
        for dir_name in self._get_dir_listing(self.shows_dir):
            dir_match = re.match(r'(.+)\s\((\d{4})\)', dir_name, re.IGNORECASE)
            if dir_match:
                dir_show_name = dir_match.group(1).strip()
                dir_variants = self._create_name_variants(dir_show_name)
                
                for show_var in show_variants:
                    for dir_var in dir_variants:
                        if show_var == dir_var or show_var in dir_var or dir_var in show_var:
                            matching_dirs.append(dir_name)
                            break
                    if dir_name in matching_dirs:
                        break
        
        if matching_dirs:
            # Prioritize US versions
            for match in matching_dirs:
                if "(US)" in match or "(USA)" in match:
                    return match
            # Otherwise use first match
            return matching_dirs[0]
            
        return None
        
    def find_best_show_directory(self, filename, show_name=None, show_year=None):
        """Find the best matching show directory for a filename."""
        if not self.shows_dir:
            return None
            
        # If show_name wasn't provided, try to extract from filename
        if not show_name:
            show_match = re.match(r'(.+?)\s*(?:-|S\d+|\()', filename, re.IGNORECASE)
            if show_match:
                show_name = show_match.group(1).strip()
            else:
                show_name = filename.split('.')[0]
                
        # Try exact matches first
        exact_matches = []
        partial_matches = []
        
        for dir_name in self._get_dir_listing(self.shows_dir):
            dir_show_name = dir_name.split('(')[0].strip().lower()
            
            # Check for exact match
            if show_name.lower() == dir_show_name:
                exact_matches.append(dir_name)
            # Check for partial match
            elif show_name.lower() in dir_show_name:
                partial_matches.append(dir_name)
                
        # Prioritize US versions from exact matches
        if exact_matches:
            for match in exact_matches:
                if "(US)" in match or "(USA)" in match:
                    return match
            # If no US version, use first exact match
            return exact_matches[0]
            
        # Fall back to partial matches
        if partial_matches:
            for match in partial_matches:
                if "(US)" in match or "(USA)" in match:
                    return match
            # If no US version, use first partial match
            return partial_matches[0]
            
        return None
