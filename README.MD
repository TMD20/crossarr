# Overview
I have a very specific need, and I decided to share this with other who may find themselves in a similar situation
1. I have a large library, and with cross-seedable torrents. However, much of this library does not have proper torrents from private trackers currently
2. I also have multiple versions of some TV shows or movies.

This script will scan your history, and utilize the data from that to match to current release via prowlarr.
The benefit to this is that it allows for all releases to be cross-seed. Even if the file has been replaced, and upgraded in sonarr/radarr

Note: 
If each TV show has it own folder, and potentially has a mix of sources. This can make matching releases that come as single episodes difficult. 
It is best if your release are full season.
    You could add this regex to must not contain to block 99 percent of all single episodes
    -> E[0-9][0-9]+
Saying that have provided limited support for single episodes as well. 

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


options
   -h, --help            Show this help message and exit.
  -c CONFIG, --config CONFIG
                        Path to a configuration file.
  --print_config [={comments,skip_null,skip_default}+]
                        Print the configuration after applying all other arguments and exit.
  -t THRESHOLD, --threshold THRESHOLD
                        The max size difference \% a match can hae (type: int, default: 1)
  -d DAYS, --days DAYS  Max Age of a release in days (type: int, default: 99999999999999999999)
  -a PROWLARRAPI, --prowlarrapi PROWLARRAPI
                        Prowlar API key (default: null)
  -p PROWLARRURL, --prowlarrurl PROWLARRURL
                        Prowlar URL (default: null)
  -f {grabbed,imported}, --flag {grabbed,imported}
                        grabbed= Releases grabbed and added to any client imported= Releases completed, and imported into library (default: imported)
  -i INDEXERS [INDEXERS ...], --indexers INDEXERS [INDEXERS ...]
                        Names of Indexer Uses Regex to Match Names (default: null)


## Example Usauge
crossarr -c aconfig radarr -u url -api a key

Take note of the order of the option it is important because of the subcommand
