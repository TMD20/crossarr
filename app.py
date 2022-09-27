#!/usr/bin/env python3
import arr.radarr as radarrAPI
import arr.sonarr as sonarrAPI
import setup.args as args
import console
import setup.logger as logger
import pathlib

userargs=args.getArgs()




print(userargs)
logger.setupLog()
console.mainConsole.print(console.Panel(f"Looking through {userargs.subcommand} for matches",style=console.normal_header_style))
#Create Folder for log and torrents




if userargs.subcommand=="sonarr":
    pathlib.Path(userargs.sonarr.folder).mkdir(parents=True, exist_ok=True)
    sonarrObj=sonarrAPI.Sonarr()
    sonarrObj.process()
else:
    pathlib.Path(userargs.radarr.folder).mkdir(parents=True, exist_ok=True)
    radarrObj=radarrAPI.Radarr()
    radarrObj.process()


    









