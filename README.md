<p align="center">
  <img src="https://raw.githubusercontent.com/mikenobbs/Asset-Assistant/main/logo/logo.png" width="500" alt="Asset-Assistant">
</p>
  
<div align="center">
  
  ![GitHub Release](https://img.shields.io/github/v/release/mikenobbs/asset-assistant?include_prereleases&display_name=release&style=flat)
  ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mikenobbs/asset-assistant/total?style=flat)
  ![GitHub Repo stars](https://img.shields.io/github/stars/mikenobbs/asset-assistant?style=flat)
  ![GitHub watchers](https://img.shields.io/github/watchers/mikenobbs/asset-assistant)
    
</div>

Asset-Assistant is a simple python script designed to categorise, move and rename artwork for your personal media server. Add 100's of images without the need to manually drag and drop them into individual directories, giving you more time to actually enjoy your media.

The script is designed primarily to use images from [TPDb](https://theposterdb.com/) and [MediUX](https://mediux.pro/) as they have a standardised naming scheme of `Title (year)`, which *should* align with naming of your media folders. The script then compares the filename with the directory name and starts the moving and renaming process. For Movies/Shows/Collections, both posters and backgrounds are supported, with the images being dynamically renamed based on their dimensions.

## Features

- Supports a range of naming schemes for popular services:
  - [Emby](https://emby.media) (coming soon)
  - [Jellyfin](https://jellyfin.org/) (coming soon)
  - [Kodi](https://kodi.tv/) (coming soon)
  - [Kometa](https://kometa.wiki/en/latest/)
  - [Plex](https://www.plex.tv/)
- Supports posters and backgrounds for Movies, Shows and Collections
- Supports season posters and episode cards for Shows
- Full logging to track which assets are moving where
- All asset categories tracked and counted
- Failed assets are backed up to be reviewed at a later time
- Optional backup for all successful moves
- Optional Discord webhook notification support

## Getting Started

### Installation

After downloading/cloning the script, unzip it to see this:
```graphql
Asset-Assistant-main
├── asset-assistant.py
├── config.yml
├── LICENSE
├── logo
│   ├── logo.png
│   └── logomark.png
├── modules
│   ├── logs.py
│   └── notifications.py
├── README.md
├── requirements.txt
└── VERSION
```

Install requirements.txt

```
pip install -r requirements.txt
```

### Config Variables

To use this script you will need to edit the following variables to your config.yml file

`process`: Directory for all your downloaded assets (emptied after every run)

`movies`: Directory that your movie assets will be moved to

`shows`: Directory where your show assets will be moved to

`collections`: Directory where your collection assets will be moved to

`enable_backup`: (Optional) true or false, false by default

`service`:  (Optional) the service that you use

`plex_specials`: (Plex users only, required) Plex specials directory naming, true or false, true = Specials, false = Season 00

`discord_webhook`: (Optional) Discord webhook URL for notifications after every run

> [!TIP]
> It's optional but don't forget to set `service`! It greatly expands the function of the script. Depending on which server you use, this setting unlocks the ability to move and rename season posters and episode cards, and even collection assets! Without it you will be limited to just Movie and TV Show assets

> [!IMPORTANT]
> While all optional variables for the `service` setting allow the use and appropriate renaming of season posters and episode cards, only `Kodi` and `Kometa` support collections currently unfortunately, this due to the other services not directly supporting local assets for collections 

### Deployment

To start this script, run

```
  python asset-assistant.py
```

## Roadmap

- Additional media server support

- Add support for .zip files

- Add more notifications options

## Disclaimer

I'm not a Python guy, heck I'm not even a coder, so take care when using this script. I tried to test every possible combination of variables but there's always a chance I missed something. I also only use Plex personally which I manage with Kometa, while I did research the other supported services I'm not as well versed on the ins and outs of them. As such, PRs are more than welcome, and if you have any issues at all feel free to post either an Issue here, or come and find me in the [TPDb Discord Server](https://discord.gg/tpdb-community-537054151583203338), DMs welcome and I'm always around 🙂

> [!Tip]
> As an extra precaution I'd recommend either setting up some dummy directories to test the script out for yourself, or running it with just a small amount of images (eg. a single show/movie/collection). This should give you a feel for how it works and let you tweak the variables if needed before unleashing it onto your entire library. 

> [!WARNING]
> Any images with conflicting filenames will be overwritten by the script, proceed with caution
    
## Support

<p><a href="https://www.buymeacoffee.com/mikenobbs"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="mikenobbs" /></a><a href="https://ko-fi.com/mikenobbs"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="mikenobbs" /></a></p><br><br>
