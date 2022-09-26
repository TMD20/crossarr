from jsonargparse import ArgumentParser, ActionConfigFile
import os

def getArgs():
    defaultconfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
    p = ArgumentParser(prog="crossarr")
    p.default_config_files = [defaultconfigPath]
    p.add_argument("-c","--config",action=ActionConfigFile)
    p.add_argument('-l', '--log', help="Where to save log file")
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
    return p.parse_args()




    
