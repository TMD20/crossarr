#!/usr/bin/env python3

import radarr.radarr as radarrAPI
import sonarr.sonarr as sonarrAPI
import args

import console



console.mainConsole.print(console.Panel(f"Looking through {args.getArgs().subcommand} for matches",style=console.normal_header_style))

if args.getArgs().subcommand=="sonarr":
    sonarrObj=sonarrAPI.Sonarr()
    sonarrObj.Process()
else:
    radarrObj=radarrAPI.Radarr()
    radarrObj.Process()


    









