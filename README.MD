# Overview

I have a very specific need, and I decided to share this with other who may find themselves in a similar situation
1. I have a large library, and with cross-seedable torrents. However, much of this library does not have proper torrents from private trackers currently
2. I also have multiple versions of some TV shows or movies. From multiple arr clients, a single arr client may grab multiple versions of a TV show/Movie

This script will scan your history, and utilize the data from that to match to current release via prowlarr.
The benefit to this is that it allows for all releases to be cross-seed. Even if the file has been replaced, and upgraded in sonarr/radarr

This is fairly easy to do with radarr as at most you only have to match one or two entries to have some confirmation that a user downloaded, and then was able to import a release into their library. 

Sonarr is a bit more of a challenge, as each episode is a different release. However, it is very helpful if you get a full season pack. As their is a lot less work to do in confirm you have the complete season. In the case of individual episodes crossarr will combine entries based on attribute. IT will then sum of the size of the release, along with compare the count of episodes to verify if a full season has been downloaded

I would recommend having Sonarr download full season only
    You could add this regex to must not contain to block 99 percent of all single episodes
    -> E[0-9][0-9]+

# How to Install/Get Started 
Instructions are provided for Linux and Windows
Older verison of python may work. but have not been tested
## Linux: 
### Required
  * python 3.9
### Install
* python3.9 -m pip install --user virtualenv
* python3.9 -m venv env
* source env/bin/activate
* which python -> should be the virtualenv
* pip3 install -r requirements.txt
* deactivate -> Do this after installing the requirements

## Windows
### Required
  * python3.9
### Install
* py -3.9 -m pip install --user virtualenv
* py -3.9 -m venv env
* .\env\Scripts\activate
* which python -> should be the virtualenv
* py -m pip install -r requirements.txt
* deactivate -> Do this after installing the requirements

## General virtualenv Guide


General Guide: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/


# Usage
## Activating Virtual Env
### Windows
* source env/bin/activate
### Linux
* .\env\Scripts\activate


 crossarr [options] sonarr [-h] [-a API] [-u URL] [-f FOLDER]
 
 or 
 
 crossarr [options] radarr [-h] [-a API] [-u URL] [-f FOLDER]



```
options
   -h, --help            Show this help message and exit.
  -c CONFIG, --config CONFIG
                        Path to a configuration file.
  --print_config [={comments,skip_null,skip_default}+]
                        Print the configuration after applying all other arguments and exit.
  -n CLIENTNAME, --clientname CLIENTNAME
                        Name of client use for logfile/lockfile sonarr or
                        raddarr use if not set (default: null)
  -v {Debug,DEBUG,debug,INFO,info,Info,off,OFF,Off}, --loglevel {Debug,DEBUG,debug,INFO,info,Info,off,OFF,Off}
                      what level to set log to flexible case-senstivity main options are [DEBUG,INFO,OFF]
                      (default: info)
  -r ROWS, --rows ROWS  Advanced Feature to set how many table rows to render
                        for Messages (default: 5)

  -t THRESHOLD, --threshold THRESHOLD
                        The max size difference \% a match can have (type: int, default: 1)
  -d DAYS, --days DAYS  Max Age of a release in days (type: int, default: 99999999999999999999)
  -a PROWLARRAPI, --prowlarrapi PROWLARRAPI
                        Prowlar API key (default: null)
  -p PROWLARRURL, --prowlarrurl PROWLARRURL
                        Prowlar URL (default: null)
  -f {grabbed,imported}, --flag {grabbed,imported}
                        grabbed= Releases grabbed and added to any client imported= Releases completed, and imported into library (default: imported)
  -i INDEXERS [INDEXERS ...], --indexers INDEXERS [INDEXERS ...]
                        Names of Indexer Uses Regex to Match Names (default: null)
  -it [0-44640], --interval [0-44640]
                        Run the script every x minutes, 0 turns off (type:
                        interval, default: 0)
                        
                        
  ```


## Example Usage
```
crossarr -c config radarr -u url -api a key
```
Take note of the order of the option it is important because of the subcommand
Basically the only thing that should come after radarr or sonarr is the url option , and api option.
Everything else needs to be before


## Interval

Only 1 instance can run per lock file name, change --clientname if you want to run instance at same time

If instance is running and next run interval time passes, that interval will be skipped. 
Program will have to wait for next interval when it finishes

Max Value:44640 Minutes=31 days

### Example

#### Times
* Interval:60 Minutes
* Runtime: 1HR 30 Minutes

First run will be at 0
Since second interval is at 60 minutes and program is still running that will be skipped
Third interval is at 2 hours. At this time program should be done running, so this interval will be ran

## LogFiles

Logfiles are saved in the logs directory. Within the same folder the program is stored
Alternately when using docker /logs folder is used to set were to mount the folder on host

# Docker

## ENV

| VAR  | DESC |
| ------------- | ------------- |
| TZ|Timezone example:America/Belem |
| CROSSARR_CLIENT|value for --clientname arg|
| CROSSARR_INTERVAL | Value for --interval arg  |


## DOCKER PATHS

| DIR| DESC |
| ------------- | ------------- |
| /logs|Directory for logfiles |
| /output|Directory for storing torrent files |
| /config|Directory with config.json|

## PASSING ARGS
use the command property of docker run or compose to pass args

## Docker Run
```
sudo docker run -it --rm -v /home/user/config.json:/config/ -v /home/user/logs/:/logs --name crossarr ghcr.io/tmd20/crossarr:main sonarr
```
## Docker Compose
As a general note you need to make an empty file/user an existing one if you want to pass docker a file, otherwise it will make a directory
```
  crossarr:
      image: ghcr.io/tmd20/crossarr:main
      container_name: crossarr
      environment:
        - TZ=enter for valid logs
      volumes:
          - /home/torrents/crossarr/config.json:/config
          - /home/torrents/crossarr/logs/:/logs/
          - /home/Downloads/Torrents:/output
      command: radarr
      restart: always
      networks:
        - mynetwork
```








# Future Updates
Support imported episodes

* Get size information from local files; I move my files to another drive, which sonarr is not aware of. 
However other user may have the file at the original location from sonarr.
* support scheduling with docker right now it only runs once it should be a daemon that runs at a interval


