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

def backup_existing_assets(dest_folder, dest_filename, backup_dir, media_name=None, delete_original=True):
    """
    Check if there are existing assets with supported extensions in the destination folder
    and back them up before overwriting.
    
    Args:
        dest_folder (str): Destination folder path
        dest_filename (str): Destination filename (without extension)
        backup_dir (str): Backup directory path
        media_name (str, optional): Media name to use in backup filename (e.g., movie/show name)
        delete_original (bool): Whether to delete the original file after backup
    
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
                # Create backup filename with media name if available
                if media_name:
                    backup_filename = f"{media_name}_backup{ext}"
                else:
                    backup_filename = f"{dest_filename}_backup{ext}"
                    
                backup_path = os.path.join(backup_dir, backup_filename)
                
                # Ensure the backup filename is unique
                counter = 1
                while os.path.exists(backup_path):
                    if media_name:
                        backup_filename = f"{media_name}_backup_{counter}{ext}"
                    else:
                        backup_filename = f"{dest_filename}_backup_{counter}{ext}"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    counter += 1
                
                # Copy to backup location
                shutil.copy2(existing_file, backup_path)
                logger.info(f" Backed up existing asset: {os.path.basename(existing_file)} → {backup_filename}")
                
                # Delete original if requested
                if delete_original:
                    try:
                        os.remove(existing_file)
                        logger.debug(f" Deleted original file after backup: {os.path.basename(existing_file)}")
                    except Exception as e:
                        logger.error(f" Failed to delete original file after backup: {e}")
                
                backed_up = True
            except Exception as e:
                logger.error(f" Error backing up existing asset: {e}")
                return False
    
    return True

def compress_and_convert_images(directory, quality=85):
    """
    Compresses and converts image files to optimized JPG format.
    
    Args:
        directory (str): Directory containing images to process
        quality (int): JPEG quality (1-100)
    
    Returns:
        int: Number of images processed
    """
    import os
    import PIL.Image
    from modules.logs import MyLogger
    logger = MyLogger()
    
    processed_count = 0
    
    logger.debug(f" Image compression settings:")
    logger.debug(f" - Directory: {directory}")
    logger.debug(f" - Quality: {quality}")
    logger.debug(f" - Supported formats: .png, .jpeg, .jpg, .bmp, .gif, .tiff")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpeg', '.bmp', '.gif', '.tiff', '.jpg')):
                original_path = os.path.join(root, file)
                # Use same filename but with .jpg extension
                new_file = os.path.splitext(file)[0] + '.jpg'
                new_path = os.path.join(root, new_file)

                try:
                    # Get original file size
                    original_size = os.path.getsize(original_path)
                    logger.debug(f" Processing '{file}':")
                    logger.debug(f" - Original size: {original_size / 1024:.2f} KB")
                    
                    with PIL.Image.open(original_path) as img:
                        # Log original image details
                        logger.debug(f" - Original dimensions: {img.width}x{img.height}")
                        logger.debug(f" - Original format: {img.format}")
                        logger.debug(f" - Original mode: {img.mode}")
                        
                        # Convert image mode if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            logger.debug(f" - Converting from {img.mode} to RGB mode")
                            img = img.convert("RGB")
                        # Save with optimization
                        img.save(new_path, 'JPEG', quality=quality, optimize=True)

                    # Get new file size and calculate compression ratio
                    if os.path.exists(new_path):
                        new_size = os.path.getsize(new_path)
                        compression_ratio = (1 - (new_size / original_size)) * 100
                        logger.debug(f" - New size: {new_size / 1024:.2f} KB")
                        logger.debug(f" - Compression ratio: {compression_ratio:.2f}%")

                    # Remove original if we changed the format
                    if new_file.lower() != file.lower():
                        logger.debug(f" - Removing original file: {file}")
                        os.remove(original_path)
                        
                    processed_count += 1
                    logger.debug(f" Successfully compressed '{file}' to optimized JPEG")
                except Exception as e:
                    logger.error(f" Failed to compress '{file}': {e}")
    
    logger.debug(f" Image compression complete. Processed {processed_count} images.")
    return processed_count
