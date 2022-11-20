import console
import setup.args as args
import re
import os
import pathlib
import setup.defaults as defaults
userargs=args.getArgs()
def logfilter(record):
    record.msg=re.sub(userargs.prowlarrapi,"prowlarrapikey",record.msg)
    if userargs.get("sonarr"):
        record.msg=re.sub(userargs.sonarr.api,"radarrapikey",record.msg)
    else:
        record.msg=re.sub(userargs.radarr.api,"sonarrapikey",record.msg)
    return True
def nologfilter(record):
    return False
    
<<<<<<< HEAD
def setupLog():
    userargs=args.getArgs()
    if not userargs.get("log"):
        userargs.log=os.path.join(pathlib.Path(os.path.realpath(__file__)).parents[1], f"{userargs.subcommand}.log")
    pathlib.Path(pathlib.Path(userargs.log).parents[0].name).mkdir(parents=True, exist_ok=True)

    
    if userargs.loglevel.upper()!="OFF":
        console.logging.getLogger(name=None).filter=logfilter
        console.logging.basicConfig(filename=userargs.log, encoding='utf-8', level=getattr(console.logging, userargs.loglevel.upper()),format='%(asctime)s:%(levelname)s:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
=======
def setupLogging():
    if userargs.loglevel.upper()!="OFF":
        console.logging.getLogger(name=None).filter=logfilter
        console.logging.basicConfig(filename=os.path.join(defaults.getLogFolder(),userargs.clientname) ,level=getattr(console.logging, userargs.loglevel.upper()),format='%(asctime)s:%(levelname)s:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
>>>>>>> origin/scheduler
    else:
        console.logging.getLogger(name=None).filter=nologfilter
