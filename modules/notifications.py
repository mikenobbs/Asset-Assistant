import requests
from datetime import datetime

def discord(summary, discord_webhook, version, total_runtime):
    if not discord_webhook:
        return
        
    current_date = datetime.now()
    image_url = "https://raw.githubusercontent.com/mikenobbs/AssetAssistant/main/logo/logomark.png"
    footer_text = f"Asset Assistant [v{version}] | {current_date.strftime('%d/%m/%Y %H:%M')} | Runtime: {total_runtime:.2f}s"
    color = 0x9E9E9E

    embed = {
        "title": "Asset Assistant",
        "description": summary,
        "thumbnail": {"url": image_url},
        "footer": {"text": footer_text},
        "color": int(color)
    }

    try:
        response = requests.post(discord_webhook, json={"embeds": [embed]})
        if response.status_code != 204:
            print(f"Failed to send Discord notification: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error sending Discord notification: {str(e)}")

def generate_summary(moved_counts, compress_images, image_quality, backup_enabled):
    summary = f"**Movie Assets:**\n {moved_counts['movie']}\n"
    summary += f"**Show Assets:**\n {moved_counts['show']}\n"
    summary += f"**Collection Assets:**\n {moved_counts['collection']}\n"
    summary += f"**Failures:**\n {moved_counts['failed']}\n"
    
    if compress_images:
        compress_text = f"True (Quality: {image_quality})"
    else:
        compress_text = "False"

    summary += f"**Compression Enabled?:**\n {compress_text}\n"

    # For backward compatibility when a single backup_enabled parameter is passed
    if isinstance(backup_enabled, bool):
        backup_source = backup_enabled
        backup_destination = backup_enabled
        backup_text = "Yes" if backup_enabled else "No"
    else:
        # Handle when we're passed a tuple of (backup_source, backup_destination)
        backup_source, backup_destination = backup_enabled
        if backup_source and backup_destination:
            backup_text = "Yes (Source & Destination)"
        elif backup_source:
            backup_text = "Yes (Source Only)"
        elif backup_destination:
            backup_text = "Yes (Destination Only)"
        else:
            backup_text = "No"
    
    summary += f"**Backup Enabled?**\n {backup_text}\n"
    return summary
