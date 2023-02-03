import re
import jellyfish
from guessit import guessit
import arrow
import console
import functools
import setup.args as args


arg=args.getArgs()
def filterMovieReleases(ele,prevDownload):
        title=prevDownload["title"]
        size=int(prevDownload["size"])
        prevDownloadInfo=guessit(title)
        releaseGroup = prevDownloadInfo.get("release_group")
        resolution = prevDownloadInfo.get("screen_size")
        quality=prevDownloadInfo.get("source")
        resolution = prevDownloadInfo.get("screen_size")
        videoCodec = prevDownloadInfo.get("video_codec")
        videoProfile = prevDownloadInfo.get("video_profile")
        filterFunctions=[functools.partial(matchByTitle,releaseGroup,title),functools.partial(matchBySize,size),functools.partial(matchQuality,quality), 
        functools.partial(matchRes,resolution),functools.partial(matchVideoCodec,videoCodec),functools.partial(matchVideoProfile,videoProfile),
        functools.partial(matchSpecial,title)
        ]
        infoDict={'title':ele['title'],'size':ele['size'],'indexer':ele['indexer'],'infourl':ele['guid']}
        console.logging.info(f"Trying to match {infoDict}")
        for funct in filterFunctions:
            if not funct(ele):
                return False
        console.logging.info(f"{ele['title']} matches completely")
        return True

def filterTVReleases(prevDownload,ele,epCount):
        title=prevDownload["title"]
        releaseData=guessit(title,"")
        releaseGroup = releaseData.get("release_group")
        resolution = releaseData.get("screen_size")
        quality=releaseData.get("source")
        resolution = releaseData.get("screen_size")
        videoCodec = releaseData.get("video_codec")
        videoProfile = releaseData.get("video_profile")
        filterFunctions=[functools.partial(matchByTitle,releaseGroup,title),functools.partial(matchQuality,quality), 
        functools.partial(matchRes,resolution),functools.partial(matchVideoCodec,videoCodec),functools.partial(matchVideoProfile,videoProfile),
        functools.partial(matchSpecial,title)
        ]
        infoDict={'title':ele['title'],'size':ele['size'],'indexer':ele['indexer'],'infourl':ele['guid']}
        console.logging.info(f"Trying to match {infoDict}")
        for funct in filterFunctions:
            if not funct(ele):
                return False
  


def matchDate(currDate,ele):
    if(matchDateHelper(currDate,ele)):
        return True
    return False
def matchDateHelper(currDate,input):
    maxAge=arg.days
    dateString=input.get("date") or input.get("publishDate")
    itemDate=arrow.get(dateString) 
    return (currDate-itemDate).days<=maxAge

def matchBySize(matchSize,ele):
    threshold=arg.threshold/100
    if abs(int(matchSize)-int(ele["size"]))/int(matchSize) <=threshold:
        console.logging.info(f"{ele['title']} size matches")
        return True
    return False


def matchBySizeSeason(seasonHistory,matchSize):
    threshold=arg.threshold/100
    season=list(filter(lambda x: re.search("E[0-9][0-9]+",x["title"],re.IGNORECASE)==None, seasonHistory))
    return list(filter(lambda x:(abs(matchSize-int(x["size"]))/matchSize)<=threshold,season))


def matchBySizeEpisodes(seasonHistory,matchSize):
    threshold=arg.threshold/100/100
    episodes=list(filter(lambda x: re.search("E[0-9][0-9]+",x["title"],re.IGNORECASE), seasonHistory))
    episodeSize=list(map(lambda x:int(x["size"]),episodes))
    if (abs(matchSize-sum(episodeSize))/matchSize)<=threshold:
        return episodes
    return []        

def matchByTitle(matchGroup,matchTitle,ele):
    eleTitle=ele["title"]
    eleGroup = ele.get("releaseGroup") or guessit(eleTitle).get("release_group")
    if eleGroup and matchGroup:
        matchGroup=titleCleanUp(matchGroup)
        eleGroup=titleCleanUp(eleGroup)
        if jellyfish.jaro_distance(matchGroup, eleGroup) < .95:
            return False
        console.logging.info(f"{ele['title']} title matches")
        return True
    elif not eleGroup and not matchGroup:
        console.logging.info(f"{ele['title']} title matches")
        return True
    else:
        return False
def titleCleanUp(title):

    title=re.sub(" +","",title)
    title=re.sub("\[","",title)
    title=re.sub("\]","",title)
    title=re.sub("\+","",title)
    title=re.sub("\*","",title)
    title=re.sub("[.-]","",title)
    title=title.lower()
    return title


def matchQuality(matchQuality,ele):
    if guessit(ele["title"]).get("source")==matchQuality:
        return True
    return False


def matchRes(res,ele):
    if not res and not guessit(ele["title"]).get("screen_size"):
        return True
    elif res==guessit(ele["title"]).get("screen_size"):
        return True
    return False
def matchVideoCodec(codec,ele):  
    if not codec and not guessit(ele["title"]).get("video_codec"):
        return True
    elif codec==guessit(ele["title"]).get("video_codec"):
        return True
    return False    

def matchVideoProfile(profile,ele):  
    if not profile and not guessit(ele["title"]).get("video_profile"):
        return True
    elif profile==guessit(ele["title"]).get("video_profile"):
        return True
    return False        

  
def matchSpecial(matchTitle,ele):
    if re.search("proper",matchTitle,re.IGNORECASE) and not re.search("proper", ele["title"],re.IGNORECASE):
        return False
    elif re.search("repack",matchTitle,re.IGNORECASE) and not re.search("repack", ele["title"],re.IGNORECASE):
        return False
    return True  

def matchSeasonNum(inputList,matchSeason):
    return list(filter(lambda x:guessit(x["title"]).get("season")==matchSeason,inputList))
 



