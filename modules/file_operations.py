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
