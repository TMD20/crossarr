from jsonargparse import ArgumentParser, ActionConfigFile
from jsonargparse.typing import restricted_number_type,restricted_string_type
import jsonargparse
import os
import pathlib

import setup.defaults as defaults


Docker_KEY = os.environ.get('CROSSARR_DOCKER', False)

interval= restricted_number_type('interval', int, [('>=', 0), ('<=', 44640)])
def setupConfig(p):
    if not Docker_KEY:
        defaultconfigPath = os.path.join(defaults.getHomeDir(),"config" ,"config.json")
        p.default_config_files = [defaultconfigPath]
        p.add_argument("-c","--config",action=ActionConfigFile)
    else:
        defaultconfigPath ="/config/config.json"
        p.default_config_files = [defaultconfigPath]
    return p

def postSetup(r):
    r.clientname=r.clientname or defaults.getClientName(r)
    r.outputs=defaults.getOutputFolder(r)
    return r
  
   


def getArgs():
    p = ArgumentParser(prog="crossarr")
    p=setupConfig(p)

    p.add_argument('-n', '--clientname', help="Name of client use for logfile/lockfile\nsonarr or raddarr use if not set",required=False)
    p.add_argument('-v', '--loglevel', help="what level to set log to flexible case-senstivity main options are [DEBUG,INFO,OFF]",type=restricted_string_type('LOG Names', '(off|debug|info)'),default="OFF")
    p.add_argument("-r","--rows",help="Advanced Feature to set how many table rows to render for Messages")
    p.add_argument("-t","--threshold",type=int,default=1,help="The max size difference \% a match can have")
    p.add_argument('-y', '--days', type=int,default=99999999999999999999,help="Max Age of a release in days")
    p.add_argument('-a', '--prowlarrapi', help="Prowlar API key")
    p.add_argument('-p', '--prowlarrurl', help="Prowlar URL")
    p.add_argument('-d', '--dryrun', help="Don't download matches", action='store_true')
    p.add_argument("-f","--flag", choices=["grabbed", "imported"],default="imported",
    help= \
    """ 
    grabbed= Releases grabbed and added to any client
    imported= Releases completed, and imported into library
    """
    )
    p.add_argument("-it","--interval",default=defaults.getDefaultInterval(),help="Run the script every x minutes, 0 turns off",type=interval,metavar="[0-44640]")
    p.add_argument("-i",'--indexers', nargs="+",help="Names of Indexer\nUses Regex to Match Names")

    radarr=ArgumentParser()
    radarr.add_argument('-a', '--api',help="radarr apikey",required=True)
    radarr.add_argument('-u', '--url',help="radarr url",required=True)
    radarr.add_argument('-f', '--folder', help="Where to save radarr torrents",required=True)
    
    sonarr = ArgumentParser()
    sonarr.add_argument('-a', '--api',help="sonarr api key",required=True)
    sonarr.add_argument('-u', '--url',help="sonarr apikey",required=True)
    sonarr.add_argument('-f', '--folder', help="Where to save sonarr torrents",required=True)

    subcommands = p.add_subcommands(help="Whether you want to scan sonarr or radarr")
    subcommands.add_subcommand('radarr', radarr)
    subcommands.add_subcommand('sonarr', sonarr)


   
    r=p.parse_args()  
    return  postSetup(r)
    
  
    





