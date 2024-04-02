import os
import shutil
import yaml
import time
import requests

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
    shutil.move(src, dest)

# Parse YAML config file
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Load directory paths from config
process_dir = config['process_dir']
shows_dir = config['shows_dir']
movies_dir = config['movies_dir']
collections_dir = config['collections_dir']
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

# Process each file in the process_dir
for filename in os.listdir(process_dir):
    destination = match_and_copy(filename, process_dir, shows_dir, movies_dir, collections_dir, failed_dir, copied_files)
    if destination:
        moved_counts[directory_names[destination]] += 1
    
    # Check if the destination directory exists
    if not os.path.exists(destination):
        print(f"Error: Destination directory '{destination}' does not exist.")
        continue
    
    # Define source and destination paths
    src = os.path.join(process_dir, filename)
    dest = os.path.join(destination, filename)
    
    # Copy the file to the destination directory
    try:
        shutil.copy(src, dest)
        print(f"File '{filename}' copied to destination successfully.")
    
        # Check if the file exists in the destination directory before moving it to the backup directory
        if os.path.exists(dest):
            try:
                shutil.move(dest, os.path.join(backup_dir, filename))
                print(f"File '{filename}' moved to backup successfully.")
            except Exception as e:
                print(f"Error moving file to backup: {e}")
        else:
            print(f"Error: File '{filename}' does not exist in the destination directory.")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Skipping.")
    except Exception as e:
        print(f"Error: {e}")
    

# Record end time
end_time = time.time()

# Calculate total runtime
total_runtime = end_time - start_time

# Move successfully copied files to backup directory if backup is enabled
if backup_enabled:
    for file_path in copied_files:
        src = os.path.join(process_dir, filename)
        shutil.move(src, os.path.join(backup_dir, filename))
  

# Create a formatted summary
summary = f"**Summary:**\n\n"
summary += f"**TV Shows:**\n {moved_counts['shows_dir']}\n"
summary += f"**Movies:**\n {moved_counts['movies_dir']}\n"
summary += f"**Collections:**\n {moved_counts['collections_dir']}\n"
summary += f"**Failures:**\n {moved_counts['failed_dir']}\n\n"
summary += f"**Backup?**\n {'Yes' if backup_enabled else 'No'}\n\n"
summary += f"**Total run time:**\n {total_runtime:.2f} seconds.\n"

# Send summary message to Discord webhook as an embed
webhook_url = config.get('webhook_url')
image_url = 
footer_text = ""
color = 0xFF0000 

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
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to send summary message to Discord.")
else:
    print("No webhook URL provided. Discord notification disabled.")

# Print summary message
print(summary)
