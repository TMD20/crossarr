from distutils.log import error
from jsonargparse import ArgumentParser, ActionConfigFile
from jsonargparse.typing import restricted_number_type,create_type
import jsonargparse
import os
import pathlib


Docker_KEY = os.environ.get('CROSSARR_DOCKER', False)

interval= restricted_number_type('interval', int, [('>=', 0), ('<=', 44640)])
def setupConfig(p):
    if not Docker_KEY:
        defaultconfigPath = os.path.join(pathlib.Path(os.path.realpath(__file__)).parents[1],"config" ,"config.json")
        p.default_config_files = [defaultconfigPath]
        p.add_argument("-c","--config",action=ActionConfigFile)
    else:
        defaultconfigPath ="/config/config.json"
        p.default_config_files = [defaultconfigPath]
    return p

def post(r):
    setupLogFile(r)
    setupOutput(r)
    setupLock(r)
    return r
def setupLogFile(r):
    name=os.environ.get('CROSSARR_CLIENT') or r.log or f"{r.subcommand}.log"
    if Docker_KEY:
        r.log=os.path.join("logs",name)
    else:
        r.log=os.path.join(pathlib.Path(os.path.realpath(__file__)).parents[1],"logs",name)
    print(r.log,Docker_KEY)
    return r
def setupOutput(r):
    if Docker_KEY:
        r[r.subcommand].folder="/output"
    return r
def setupLock(r):
    r.lock= os.path.join(pathlib.Path(os.path.realpath(__file__)).parents[1],r.lock)
    return r
def getDefaultInterval():
    if os.environ.get('CROSSARR_INTERVAL'):
        return int(os.environ.get('CROSSARR_INTERVAL'))
    return 0

def getArgs():
    p = ArgumentParser(prog="crossarr")
    p=setupConfig(p)
    
  
    p.add_argument('-l', '--log', help="name of log file")
    p.add_argument('-v', '--loglevel', help="what level to set log to flexible case-senstivity main options are [DEBUG,INFO,OFF]",choices=["Debug","DEBUG","debug","INFO","info","Info","off","OFF","Off"],default="OFF")
    p.add_argument("-r","--rows",help="Advanced Feature to set how many table rows to render for Messages",default=5)
    p.add_argument("-t","--threshold",type=int,default=1,help="The max size difference \% a match can have")
    p.add_argument('-d', '--days', type=int,default=99999999999999999999,help="Max Age of a release in days")
    p.add_argument('-a', '--prowlarrapi', help="Prowlar API key")
    p.add_argument('-p', '--prowlarrurl', help="Prowlar URL")
    p.add_argument("-f","--flag", choices=["grabbed", "imported"],default="imported",
    help= \
    """ 
    grabbed= Releases grabbed and added to any client
    imported= Releases completed, and imported into library
    """
    )
    p.add_argument("-lk","--lock",default="crossarr.lock",help="File Lock to prevent multiple instances")
    p.add_argument("-it","--interval",default=getDefaultInterval(),help="Run the script every x minutes, 0 turns off",type=interval,metavar="[0-44640]")

    p.add_argument("-i",'--indexers', nargs="+",help="Names of Indexer\nUses Regex to Match Names")

    radarr=ArgumentParser()
    radarr.add_argument('-a', '--api',help="radarr apikey")
    radarr.add_argument('-u', '--url',help="radarr url")
    radarr.add_argument('-f', '--folder', help="Where to save radarr torrents")
    
    sonarr = ArgumentParser()
    sonarr.add_argument('-a', '--api',help="sonarr api key")
    sonarr.add_argument('-u', '--url',help="sonarr apikey")
    sonarr.add_argument('-f', '--folder', help="Where to save sonarr torrents")

    subcommands = p.add_subcommands(help="Whether you want to scan sonarr or radarr")
    subcommands.add_subcommand('radarr', radarr)
    subcommands.add_subcommand('sonarr', sonarr)

   
    r=p.parse_args()
    subspace=r.get(r.subcommand)
    if not subspace.api:
        raise jsonargparse.ParserError(f"{r.subcommand}.api","can't be null")
    if not subspace.folder:
        raise jsonargparse.ParserError(f"{r.subcommand}.folder","can't be null")
    if not subspace.url:
        raise jsonargparse.ParserError(f"{r.subcommand}.url","can't be null")    
    return post(r)
    
  
    





