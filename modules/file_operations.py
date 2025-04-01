"""
File operations for Asset Assistant.
Contains functions for moving, copying, and backup operations.
"""
import os
import shutil
import zipfile
from modules.logs import MyLogger

logger = MyLogger()

def unzip_files(process_dir, failed_dir):
    """Extract all zip files in the process directory."""
    for item in os.listdir(process_dir):
        if item.lower().endswith('.zip'):
            file_path = os.path.join(process_dir, item)
            try:
                logger.info(f" Processing zip file '{item}'")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(process_dir)
                os.remove(file_path)
                logger.info(" - Successfully extracted")
                logger.info("")
            except zipfile.BadZipFile:
                logger.error(f" - '{item}' is not a valid zip file")
                move_to_failed(item, process_dir, failed_dir)
                logger.info(" - Moved to failed directory")
                logger.info("")
            except Exception as e:
                logger.error(f" - Error extracting '{item}': {str(e)}")
                move_to_failed(item, process_dir, failed_dir)
                logger.info(" - Moved to failed directory")
                logger.info("")

def process_directories(process_dir):
    """Process subdirectories by moving their contents to the main directory."""
    for item in os.listdir(process_dir):
        item_path = os.path.join(process_dir, item)
        if os.path.isdir(item_path):
            for root, _, files in os.walk(item_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        src = os.path.join(root, file)
                        dest = os.path.join(process_dir, file)
                        shutil.move(src, dest)
            shutil.rmtree(item_path)
            logger.info(f" Processing folder '{item}'")
            logger.info("")

def move_to_failed(filename, process_dir, failed_dir):
    """Move a file to the failed directory."""
    src = os.path.join(process_dir, filename)
    dest = os.path.join(failed_dir, filename)
    
    try:
        shutil.move(src, dest)
    except FileNotFoundError:
        logger.error(" - File not found during move to failed directory")
    except PermissionError:
        logger.error(" - Permission denied when moving to failed directory")
    except Exception as e:
        logger.error(f" - Failed to move to failed directory: {e}")

def backup_file(filename, process_dir, backup_dir):
    """Backup a file to the backup directory."""
    src = os.path.join(process_dir, filename)
    dest = os.path.join(backup_dir, filename)
    
    try:
        shutil.move(src, dest)
        logger.info(f" - Moved '{filename}' to backup directory")
    except FileNotFoundError:
        logger.error(f" - File '{filename}' not found during backup")
    except PermissionError:
        logger.error(f" - Permission denied when backing up '{filename}'")
    except Exception as e:
        logger.error(f" - Failed to backup '{filename}' to backup directory: {e}")

def copy_file(src, dest, filename=None):
    """Copy a file from src to dest."""
    try:
        shutil.copy(src, dest)
        return True
    except FileNotFoundError:
        filename = filename or os.path.basename(src)
        logger.error(f" - File '{filename}' not found during copy")
    except PermissionError:
        filename = filename or os.path.basename(src)
        logger.error(f" - Permission denied when copying '{filename}'")
    except Exception as e:
        filename = filename or os.path.basename(src)
        logger.error(f" - Failed to copy '{filename}': {e}")
    return False

def rename_file(old_path, new_path):
    """Rename a file."""
    try:
        os.rename(old_path, new_path)
        return True
    except FileNotFoundError:
        logger.error(f" - File not found during rename")
    except PermissionError:
        logger.error(f" - Permission denied when renaming")
    except Exception as e:
        logger.error(f" - Failed to rename: {e}")
    return False

def delete_file(path):
    """Delete a file."""
    try:
        os.remove(path)
        logger.info(" - Deleted from process directory")
        return True
    except FileNotFoundError:
        logger.error(" - File not found during deletion")
    except PermissionError:
        logger.error(" - Permission denied when deleting")
    except Exception as e:
        logger.error(f" - Failed to delete: {e}")
    return False

def backup_existing_assets(dest_folder, dest_filename, backup_dir):
    """
    Check if there are existing assets with supported extensions in the destination folder
    and back them up before overwriting.
    
    Args:
        dest_folder (str): Destination folder path
        dest_filename (str): Destination filename (without extension)
        backup_dir (str): Backup directory path
    
    Returns:
        bool: True if successful or no existing assets, False if backup failed
    """
    from modules.logs import MyLogger
    logger = MyLogger()
    
    # Supported extensions to check for
    supported_extensions = ('.jpg', '.jpeg', '.png')
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            logger.error(f" Error creating backup directory: {e}")
            return False
            
    # Check for existing assets with the same name but any supported extension
    backed_up = False
    
    for ext in supported_extensions:
        existing_file = os.path.join(dest_folder, dest_filename + ext)
        if os.path.exists(existing_file):
            logger.debug(f" Found existing asset: {existing_file}")
            try:
                # Create backup filename with _backup suffix
                backup_basename = os.path.basename(dest_folder)
                backup_filename = f"{dest_filename}_backup{ext}"
                backup_path = os.path.join(backup_dir, backup_filename)
                
                # Ensure the backup filename is unique
                counter = 1
                while os.path.exists(backup_path):
                    backup_filename = f"{dest_filename}_backup_{counter}{ext}"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    counter += 1
                
                # Copy to backup location
                shutil.copy2(existing_file, backup_path)
                logger.info(f" Backed up existing asset: {os.path.basename(existing_file)} → {backup_filename}")
                backed_up = True
            except Exception as e:
                logger.error(f" Error backing up existing asset: {e}")
                return False
    
    return True
