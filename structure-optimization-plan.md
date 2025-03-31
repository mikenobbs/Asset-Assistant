# Asset Assistant - Code Structure Optimization Plan

After analyzing the current codebase, I've identified several opportunities to improve the code structure by making it more modular, maintainable, and following better software design principles. Below is the plan for restructuring:

## Current Issues

1. **Monolithic Design**: The entire application is in a single file with large functions
2. **Lack of Modularity**: Business logic, utilities, and configuration are mixed together
3. **Repeated Code Patterns**: Similar matching logic is duplicated in multiple places
4. **Complex Conditional Logic**: Many nested if-statements making the code hard to follow
5. **Poor Separation of Concerns**: File operations, media matching, and configuration are intermingled

## New Structure

I've created a more modular approach by splitting functionality into specific modules:

### 1. `modules/file_operations.py`

A module dedicated to file system operations:
- `unzip_files()`: Extract zip files in the process directory
- `process_directories()`: Process subdirectories 
- `move_to_failed()`: Move a file to the failed directory
- `backup_file()`: Backup a file to the backup directory
- `copy_file()`: Copy a file with proper error handling
- `rename_file()`: Rename a file with proper error handling
- `delete_file()`: Delete a file with proper error handling

### 2. `modules/media_matcher.py`

A module focused on matching media files with appropriate directories:
- `MediaMatcher` class:
  - `match_media()`: Determine file category and extract metadata
  - `_find_movie_match()`: Find matching movie directory
  - `_find_collection_match()`: Find matching collection directory
  - `_find_show_directory()`: Find matching TV show directory
  - `find_best_show_directory()`: Find best matching show directory using multiple strategies
  - `_create_name_variants()`: Create different name variants for better matching

### 3. `modules/config_manager.py`

A module for managing configuration:
- `ConfigManager` class:
  - `load_config()`: Load configuration from files or environment variables
  - `_load_config_from_env()`: Load configuration from environment variables
  - `_validate_config()`: Validate configuration parameters
  - `_log_config()`: Log the current configuration

### 4. `modules/asset_processor.py`

A module responsible for processing assets:
- `AssetProcessor` class:
  - `process_asset()`: Process a single asset file
  - `_handle_failed()`: Handle files that couldn't be categorized
  - `_process_movie_or_show()`: Process movie or show posters
  - `_process_collection()`: Process collection assets
  - `_process_kometa_season()`: Process season posters for Kometa
  - `_process_kometa_episode()`: Process episode assets for Kometa
  - `_process_plex_season()`: Process season posters for Plex
  - `_process_plex_episode()`: Process episode assets for Plex

### 5. `asset-assistant.py` (Main script)

The main script is now much cleaner:
- Improved organization with clear sections
- Better imports and module utilization
- Simplified flow with clearer responsibilities
- Uses the modular components we've created

## Benefits of This Structure

1. **Better Separation of Concerns**: Each module has a specific responsibility
2. **Enhanced Maintainability**: Smaller, focused files are easier to understand and modify
3. **Improved Testability**: Components can be tested separately
4. **Reduced Duplication**: Common functionality is centralized
5. **Clearer Structure**: Code organization makes logical sense
6. **Easier Extensions**: Adding new features or media servers would be more straightforward

## Implementation Strategy

To implement these changes:
1. Create the new module files with the refactored code
2. Update the main script to use the new modules
3. Test the application to ensure functionality remains the same
4. Update any documentation to reflect the new structure
