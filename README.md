<p align="center">
  <img src="https://raw.githubusercontent.com/mikenobbs/Asset-Assistant/main/logo/logo.png" width="500" alt="Asset-Assistant">
</p>
  
<div align="center">
  
  [![GitHub Release](https://img.shields.io/github/v/release/mikenobbs/asset-assistant?include_prereleases&display_name=release&style=flat)](https://github.com/mikenobbs/Asset-Assistant/releases)
  [![GitHub Repo stars](https://img.shields.io/github/stars/mikenobbs/asset-assistant?style=flat)](https://github.com/mikenobbs/Asset-Assistant/stargazers)
  [![GitHub watchers](https://img.shields.io/github/watchers/mikenobbs/asset-assistant)](https://github.com/mikenobbs/Asset-Assistant/watchers)
    
</div>

<p align="center">
  <a href="https://ko-fi.com/mikenobbs" target="_blank"><img src="https://images2.imgbox.com/ad/d8/0Ulu9hEi_o.png" width="250" alt="Support Me On Ko-Fi"/></a>
</p>

**AssetAssistant** is a simple python script designed to categorise, move and rename artwork for your personal media server. Add 1000's of images without the need to manually drag and drop them into individual directories, giving you more time to actually enjoy your media.

The script is designed primarily to use images from [The Poster Database (TPDb)](https://theposterdb.com/) and [MediUX](https://mediux.pro/) as they use a straightforward naming scheme of `Title (year)`, which *should* align with naming of your media folders. The script then compares the filename with the directory name and starts the moving and renaming process. For Movies/Shows/Collections, both posters and backgrounds are supported, with the images being dynamically renamed based on their dimensions. Season and episode renaming is dependent on the service you are using.

> [!TIP]
> Using [Sonarr](https://sonarr.tv/)/[Radarr](https://radarr.video/) combined with [TRaSH Guides](https://trash-guides.info/) will give you the best possible outcome, as the script was written with TRaSH's naming convention in mind.

> [!IMPORTANT]
> One of the main points of failure is going to be collection assets. This is partly down to the loose way in which they are detected, but mainly the issue is going to be any discrepencies between what you've called your collections and what they're called on TPDb/MediUX. Fortunately, failed assets are moved to a separate directory for you to either rename and try again, or move manually 🙂

## Features

- Supports a range of naming schemes for popular services:
  - [Emby](https://emby.media) (coming soon)
  - [Jellyfin](https://jellyfin.org/) (coming soon)
  - [Kodi](https://kodi.tv/) (coming soon)
  - [Kometa](https://kometa.wiki/en/latest/)
  - [Plex](https://www.plex.tv/)
- Supports posters and backgrounds for Movies, Shows and Collections
- Supports season posters and episode cards for Shows
- Supports .zip files as well as subdirectories within the process directory
- Full logging to track which assets are moving where
- All asset categories tracked and counted
- Failed assets are backed up to be reviewed at a later time
- Optional backup for all successful moves
- Optional backup for any existing assets
- Optional image compression with adjustable quality
- Optional Discord webhook notification support

## Getting Started

### Installation

After downloading/cloning the repo, unzip the file to see this directory structure:
```graphql
Asset-Assistant-main
├── asset-assistant.py
├── config.yml
├── Dockerfile
├── entrypoint.sh
├── LICENSE
├── logo
│   ├── logo.png
│   └── logomark.png
├── modules
│   ├── asset_processor.py
│   ├── config_manager.py
│   ├── file_operations.py
│   ├── logs.py
│   ├── media_matcher.py
│   └── notifications.py
├── README.md
├── requirements.txt
├── VERSION
├── .dockerignore
└── .github
    ├── FUNDING.yml
    └── workflows
        └── docker.yml
```

Open a terminal/CMD window in this directory and install requirements.txt

```
pip install -r requirements.txt
```

### Config Variables

To use this script you will need to edit the following variables in your config.yml file

`process`: (Optional - defaults to script directory) Directory for all your downloaded assets (emptied after every run)

`movies`: Directory that your movie assets will be moved to

`shows`: Directory where your show assets will be moved to

`collections`: Directory where your collection assets will be moved to

`failed`: (Optional - defaults to script directory) Directory for failed assets

`logs`: (Optional - defaults to script directory) Directory for run logs

`backup`: (Optional - defaults to script directory) Directory for backups

`enable_backup_source`: (Optional) Backup for new assets

`enable_backup_destination`: (Optional) Backup for existing assets

`service`:  (Optional) The media service that you use

`plex_specials`: (Plex users only, required) Plex specials directory naming

`compress_images`: (Optional) Compress and optimize your assets

`image_quality`: (Optional) The quality of the resulting JPEG

`debug`: (Optional) Enable for more detailed logging

`discord_webhook`: (Optional) Discord webhook URL for notifications after every run

> [!IMPORTANT]
> All directories (process/movies/shows/collections) must be unique for the script to function properly. For `Kodi`, this guide [here](https://kodi.wiki/view/Movie_set_information_folder) outlines the collection directory process, which you'll want to point **AssetAssistant** at. For `Kometa`, you may need to adjust your setup slightly in order to achieve the separate directories. Below is an example of how to achieve this:
> ```yml
> libraries:
>   Movies:
>     collection_files:
>       - file: config/movies1.yml
>         asset_directory: config/assets/collections
>       - file: config/movies2.yml
>         asset_directory: config/assets/collections
>     settings:
>       asset_directory: config/assets/movies
>   TV Shows:
>     collection_files:
>       - repo: config/tv1.yml
>         asset_directory: config/assets/collections
>       - repo: config/tv2.yml
>         asset_directory: config/assets/collections
>     settings:
>       asset_directory: config/assets/tv
> ```
> Notice that while the main asset directory for each library is `movies/tv`, I specify that each collection yml is actually pointing at `config/assets/collections`.

> [!NOTE]
> While optional, setting the `service` variable greatly expands the functionality of AA. Depending on which service you use, this setting unlocks the ability to move and rename season posters and episode cards, and even collection assets. Without it you will be limited to just movie and show assets. Please note that currently only `Kodi` and `Kometa` support collection assets unfortunately. This is due to the other services not directly supporting local assets for collections.

> [!WARNING]
> All assets will be removed from `process` after each run. In case of any incorrect moves I highly recommend using `enable_backup_source: true`.

### Deployment

From the script directory, run

```
  python asset-assistant.py
```
to start **AssetAssistant**

## Docker

Compose
```yml
asset-assistant:
  image: mikenobbs/asset-assistant
  container_name: asset-assistant
  environment:
    - ENABLE_BACKUP_SOURCE=false
    - ENABLE_BACKUP_DESTINATION=false
    - SERVICE=plex
    - PLEX_SPECIALS=false
    - COMPRESS_IMAGES=false
    - IMAGE_QUALITY=85
    - DEBUG=false
  volumes:
    - /<host_folder_config>:/config
```
You would then also need to mount your various directories, for example:
```yml
- /<host_folder_movies>:/config/movies
- /<host_folder_shows>:/config/shows
- /<host_folder_collections>:/config/collections
```
Or, if the directories are all within the same parent directory you could just use a single mount for convenience:
```yml
- /<host_folder_assets>:/config/assets
```
Remember to set these paths in your config.yml as well, and to do similar if you wish to change the location of the `process`, `failed`, `logs` and `backup`directories.

## Roadmap

- Additional media server support

- Add more notifications options

- A web UI

- Scheduling

- "Integration" 👀

## Disclaimer

I'm not a Python guy, heck I'm not even a coder, so take care when using this script. I tried to test every possible combination of variables but there's always a chance I missed something. I also personally only use Plex which I manage with Kometa, and while I did research the other supported services, I'm not as well versed on the ins and outs of them. As such, [PRs](https://github.com/mikenobbs/Asset-Assistant/pulls) are more than welcome, and if you have any issues at all feel free to post either an [Issue](https://github.com/mikenobbs/Asset-Assistant/issues), or come and find me in the [TPDb Discord Server](https://discord.gg/tpdb-community-537054151583203338), DMs welcome and I'm always around 🙂

> [!Tip]
> As an extra precaution I'd recommend either setting up some dummy directories to test **AssetAssistant** out for yourself, or running it with just a small amount of images (eg. a single show/movie/collection). This should give you a feel for how it works and let you tweak the variables if needed before unleashing it onto your entire library. 

> [!WARNING]
> Any images with conflicting filenames will be removed by the script to avoid any conflicts, set `enable_backup_destination: true` as an extra layer of protection.

## Special Thanks

First, to my friend **haydensnow**, whose [posterpal](https://github.com/haydensnow/posterpal) script started all of this. If I hadn't decided to tinker with it, **AssetAssistant** would never have been born. Secondly, huge thanks to [jrelax](https://github.com/jrelax) for his work refactoring the script, getting the docker container up and running, as well as adding a bunch of additional features. All the work has inspired me to start on this project again. And finally a shoutout to the guys over at [Kometa](https://github.com/Kometa-Team/Kometa), who unintentionally inspired me with their logs, they look great so I made it my mission to replicate them best I could 😅
