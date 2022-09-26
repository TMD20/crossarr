#!/usr/bin/env python3
import re

import arr.radarr as radarrAPI
import arr.sonarr as sonarrAPI
import args
import console
import logger


    

userargs=args.getArgs()
logger.setupLog()
console.mainConsole.print(console.Panel(f"Looking through {userargs.subcommand} for matches",style=console.normal_header_style))

if userargs.subcommand=="sonarr":
    sonarrObj=sonarrAPI.Sonarr()
    sonarrObj.process()
else:
    radarrObj=radarrAPI.Radarr()
    radarrObj.process()


    









