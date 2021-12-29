# Panopto Downloader
## Disclaimer
You should check with your university if you are allowed to download recordings using this tool.

## Installation
### Requirements
Note: you must have https://ffmpeg.org/ installed

```
pip install -r requirements.txt
```

## Usage
### Modes
There are currently two modes, visible_videos and open_tabs. open_tabs will only choose to download videos from tabs you have currently opened. visible_videos will download all of the videos in the current window view.

### Arguments
| Argument              | Type | Description                                                                                                                                              | Required | Default                |
|-----------------------|------|----------------------------------------------------------------------------------------------------------------------------------------------------------|----------|------------------------|
| -url                  | str  | base url of your institutions panopto service <br /> example: https://imperial.cloud.panopto.eu                                                                                    | YES      | NONE                   |
| -mode                 | str  | mode of extracting videos to download <br /> select from ["visible_videos", "open_tabs"]                                                                        | NO       | visible_videos         |
| -outdir               | str  | directory to save all videos to                                                                                                                          | NO       | out                    |
| --chrome-profile-path | str  | path for chrome profile (to minimise signing in)  <br /> read: https://www.howtogeek.com/255653/how-to-find-your-chrome-profile-folder-on-windows-mac-and-linux/ | NO       | NONE                   |
| --num-threads         | int  | number of threads in thread pool                                                                                                                         | NO       | see ThreadPoolExecutor |
### Examples

```
// Download all visible videos
python panoptoDownloader.py -url <url>

// Download open tabs with specified path
python panoptoDownloader.py -url <url> -mode open_tabs --chrome-profile-path <path>
```
