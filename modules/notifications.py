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

def generate_summary(moved_counts, backup_enabled, total_runtime, version):
    summary = f"**Movie Assets:**\n {moved_counts['movie']}\n"
    summary += f"**Show Assets:**\n {moved_counts['show']}\n"
    summary += f"**Collection Assets:**\n {moved_counts['collection']}\n"
    summary += f"**Failures:**\n {moved_counts['failed']}\n"
    summary += f"**Backup Enabled?**\n {backup_enabled}\n"
    summary += f"**Total Run Time:**\n {total_runtime:.2f} seconds\n"
    summary += f"**Version:**\n v{version}\n"
    return summary
