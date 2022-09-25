#!/usr/bin/env python3

import arr.radarr as radarrAPI
import arr.sonarr as sonarrAPI
import args

import console



console.mainConsole.print(console.Panel(f"Looking through {args.getArgs().subcommand} for matches",style=console.normal_header_style))

if args.getArgs().subcommand=="sonarr":
    sonarrObj=sonarrAPI.Sonarr()
    sonarrObj.process()
else:
    radarrObj=radarrAPI.Radarr()
    radarrObj.process()


    









