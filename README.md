# <img src="https://raw.githubusercontent.com/mikenobbs/Asset-Assistant/main/logo/logo.png" alt="Asset-Assistant">

![GitHub Release](https://img.shields.io/github/v/release/mikenobbs/asset-assistant?include_prereleases&display_name=release&style=flat)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mikenobbs/asset-assistant/total?style=flat)
![GitHub Repo stars](https://img.shields.io/github/stars/mikenobbs/asset-assistant?style=flat)
![GitHub watchers](https://img.shields.io/github/watchers/mikenobbs/asset-assistant)

Asset-Assistant is a simple python script designed to categorise, move and rename artwork for your personal media server. Add 100's of images without the need to manually drag and drop them into individual directories, giving you kore time to actually enjoy your media.



## Features

- Supports posters and backgrounds for Movies, TV Shows and Collections
- Supports season posters and episode cards
- Full logging to track which assets are moving where
- All assets categories tracked and counted
- Failed assets are backed up to be reviewed at a later time
- Optional backup for all successful moves
- Optional Discord webhook notification support

## Getting Started

#### Installation

Install requirements.txt

```
pip install -r requirements.txt
```

#### Config Variables

To use this script you will need to add the following variables to your config.yml file

`process`: Directory for all your downloaded assets (emptied after every run)

`movies`: Directory that your movie assets will be moved to

`shows`: Directory where your show assets will be moved to

`collections`: Directory where your collection assets will be moved to

`enable_backup`: (Optional) true or false, false by default

`media_server`:  (Optional) your media server of choice, select yours from the available options to have your assets named correctly (if left unset only movie and show assets will be support, currently only `Kometa` supports collection assets)

`plex_specials`: (Plex users only, required) Plex specials directory naming, true or false, true = Specials, false = Season 00

`discord_webhook`: (Optional) Discord webhook URL for notifications after every run

#### Deployment

To start this script, run

```
  python asset-assistant.py
```

## Roadmap

- Additional media server support

- Add support for .zip files

- Add more notifications options

## Disclaimer

I'm not a Python guy, heck I'm not even a coder. As such, take care when using this script. I tried to test every possible combination of variables but as an extra precaution I'd recommend either setting up some dummy directories to test it out for yourself, or running it with just a small amount of images (eg. a single show/movie/collection). This should give you a feel for how it works and let you tweak the variables if needed before unleashing it onto your entire library. Please note, any images with conflicting names will be overwritten by the script, proceed with caution.
    
## Support

<p><a href="https://www.buymeacoffee.com/mikenobbs"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="mikenobbs" /></a><a href="https://ko-fi.com/mikenobbs"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="mikenobbs" /></a></p><br><br>
