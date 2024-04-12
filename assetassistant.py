import os
import shutil
import yaml
import time
import requests
from datetime import datetime


# Parse YAML config file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Load directory paths from config
process_dir = config['process']
shows_dir = config['shows']
movies_dir = config['movies']
collections_dir = config['collections']
script_dir = os.path.dirname(os.path.abspath(__file__))
failed_dir = os.path.join(script_dir, 'failed')
backup_enabled = config.get('enable_backup', False)
backup_dir = os.path.join(script_dir, 'backup')

# Create failed directory if it doesn't exist
if not os.path.exists(failed_dir):
    os.makedirs(failed_dir)

# Create backup directory if backup is enabled and it doesn't exist
if backup_enabled and not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Match filename with directory names and copy the file
def match_and_copy(filename, process_dir, shows_dir, movies_dir, collections_dir, failed_dir, copied_files):
    # Extract name and year from filename
    name, ext = os.path.splitext(filename)
    parts = name.split('(')
    if len(parts) >= 2:
        # If filename contains parentheses, search in shows and movies directories
        title = parts[0].strip()
        year = parts[1].split(')')[0].strip()
        for directory in [shows_dir, movies_dir]:
            for dir_name in os.listdir(directory):
                if f"{title} ({year})" in dir_name:
                    # Copy the file to the matching directory
                    src = os.path.join(process_dir, filename)
                    dest = os.path.join(directory, dir_name, filename)
                    shutil.copy(src, dest)
                    copied_files.append(dest)
                    return directory
    else:
        # If filename doesn't contain parentheses, search in collections directory
        for dir_name in os.listdir(collections_dir):
            if "Collection" in name:
                name_without_collection = name.replace("Collection", "").strip()
                if name_without_collection in dir_name:
                    # Copy the file to the matching directory
                    src = os.path.join(process_dir, filename)
                    dest = os.path.join(collections_dir, dir_name, filename)
                    shutil.copy(src, dest)
                    copied_files.append(dest)
                    return collections_dir
            else:
                if name in dir_name:
                    # Copy the file to the matching directory
                    src = os.path.join(process_dir, filename)
                    dest = os.path.join(collections_dir, dir_name, filename)
                    shutil.copy(src, dest)
                    copied_files.append(dest)
                    return collections_dir

    # If no matching directory is found, move to failed directory
    move_to_failed(filename, process_dir, failed_dir)
    return None

# Function to move the file to the failed directory
def move_to_failed(filename, process_dir, failed_dir):
    src = os.path.join(process_dir, filename)
    dest = os.path.join(failed_dir, filename)
    shutil.copy(src, dest)

# List to store successfully copied files
copied_files = []

# Counters for images moved to different directories
moved_counts = {'shows_dir': 0, 'movies_dir': 0, 'collections_dir': 0, 'failed_dir': 0}

# Record start time
start_time = time.time()

directory_names = {
    shows_dir: 'shows_dir',
    movies_dir: 'movies_dir',
    collections_dir: 'collections_dir',
    failed_dir: 'failed_dir'
}
            
for filename in os.listdir(process_dir):
    destination = match_and_copy(filename, process_dir, shows_dir, movies_dir, collections_dir, failed_dir, copied_files)
    if destination:
        moved_counts[directory_names[destination]] += 1

# Record end time
end_time = time.time()

# Calculate total runtime
total_runtime = end_time - start_time

# Copy successfully copied files to backup directory if backup is enabled
if backup_enabled:
    for file_path in copied_files:
        shutil.copy(file_path, os.path.join(backup_dir, os.path.basename(file_path)))
        
# Remove all files from process_dir
for filename in os.listdir(process_dir):
    file_path = os.path.join(process_dir, filename)
    os.remove(file_path)

# Create a formatted summary
summary = f"**Movie Posters:**\n {moved_counts['movies_dir']}\n"
summary += f"**TV Show Posters:**\n {moved_counts['shows_dir']}\n"
summary += f"**Collection Posters:**\n {moved_counts['collections_dir']}\n"
summary += f"**Failures:**\n {moved_counts['failed_dir']}\n"
summary += f"**Backup Enabled?**\n {'Yes' if backup_enabled else 'No'}\n"
summary += f"**Total Run Time:**\n {total_runtime:.2f} seconds\n"

# Get the current date
current_date = datetime.now().date()

# Read the script version from version.txt
version = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version, 'r') as f:
    script_version = f.read().strip()
    
# Send summary message to Discord webhook as an embed
webhook_url = config.get('webhook_url')
image_url = "https://raw.githubusercontent.com/mikenobbs/AssetAssistant/main/logo/icon.png"
footer_text = f"AssetAssistant [v{script_version}] | {current_date.strftime('%d/%m/%Y %H:%M')}"
color = 0x9E9E9E

if webhook_url:
    # Construct the embed object with custom values
    embed = {
        "title": "Asset Assistant",
        "description": summary,
        "image": {"url": image_url},
        "footer": {"text": footer_text},
        "color": color
    }
    
    # Send the embed data to the Discord webhook using a POST request
    response = requests.post(webhook_url, json={"embeds": [embed]})
