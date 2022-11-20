import os
import pathlib
Docker_KEY = os.environ.get('CROSSARR_DOCKER', False)


def getClientName(r):
    return os.environ.get('CROSSARR_CLIENT') or r.clientname or f"{r.subcommand}.log"

def getLogFolder():
    if Docker_KEY:
        return "/logs"
    else:
        return os.path.join(getHomeDir(),"logs")

def getHomeDir():
    return pathlib.Path(os.path.realpath(__file__)).parents[1]
def getOutputFolder(r):
   
    if Docker_KEY:
        return "/output"
    return r[r.subcommand].folder
def setupLockFolder(r):
    return os.path.join(pathlib.Path(os.path.realpath(__file__)).parents[1])

def getDefaultInterval():
    if os.environ.get('CROSSARR_INTERVAL'):
        return int(os.environ.get('CROSSARR_INTERVAL'))
    return 0