import requests
from datetime import datetime

def discord(summary, discord_webhook, version, total_runtime):
    current_date = datetime.now()
    image_url = "https://raw.githubusercontent.com/mikenobbs/AssetAssistant/main/logo/logomark.png"
    footer_text = f"Asset Assistant [v{version}] | {current_date.strftime('%d/%m/%Y %H:%M')}"
    color = 0x9E9E9E

    embed = {
        "title": "Asset Assistant",
        "description": summary,
        "thumbnail": {"url": image_url},
        "footer": {"text": footer_text},
        "color": color
    }

    response = requests.post(discord_webhook, json={"embeds": [embed]})

def generate_summary(moved_counts, backup_enabled, total_runtime, version):
    summary = f"**Movie Assets:**\n {moved_counts['movies_dir']}\n"
    summary += f"**Show Assets:**\n {moved_counts['shows_dir']}\n"
    summary += f"**Collection Assets:**\n {moved_counts['collections_dir']}\n"
    summary += f"**Failures:**\n {moved_counts['failed_dir']}\n"
    summary += f"**Backup Enabled?**\n {'Yes' if backup_enabled else 'No'}\n"
    summary += f"**Total Run Time:**\n {total_runtime:.2f} seconds\n"
    return summary
