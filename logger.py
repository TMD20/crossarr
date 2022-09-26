import console
import args
import re

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
    
def setupLog():
    userargs=args.getArgs()


    if userargs.loglevel.upper()!="OFF":
        console.logging.getLogger(name=None).filter=logfilter
        console.logging.basicConfig(filename=userargs.log, encoding='utf-8', level=getattr(console.logging, userargs.loglevel.upper()),format='%(asctime)s:%(levelname)s:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    else:
        console.logging.getLogger(name=None).filter=nologfilter
