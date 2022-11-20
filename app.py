#!/usr/bin/env python3
import arr.radarr as radarrAPI
import arr.sonarr as sonarrAPI
import setup.args as args
import console
import setup.logger as logger
import pathlib
import portalocker
import schedule
import time
import threading
import os



def run_threaded(job_func,userargs):
    job_thread = threading.Thread(target=job_func,args=[userargs])
    job_thread.start()


def run(userargs):
    try:
        with portalocker.Lock(userargs.lock,fail_when_locked=True, timeout=1000) as fh:
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
    except Exception as E:
        if isinstance(E,portalocker.exceptions.AlreadyLocked): 
            #Fix Later to use rich if possible
            print(E)
            console.logging.info(str(E))

        else:
            print(E)
            os.remove(userargs.lock)
      
def main():
    logger.setupLogging()

    userargs=args.getArgs()
    if userargs.interval>0:
        console.mainConsole.print(console.Panel(f"Running Every {userargs.interval} Minutes",style=console.normal_header_style))
        schedule.every(userargs.interval).minutes.do(run_threaded,run,userargs=userargs)
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        run(userargs)



if __name__ == '__main__':
    main()
 









