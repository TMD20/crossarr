import re
import jellyfish
import datetime
from guessit import guessit
import arrow


def matchBySizeSeason(inputList,matchSize,threshold):
    threshold=threshold/100
    season=list(filter(lambda x: re.search("E[0-9][0-9]+",x["sourceTitle"],re.IGNORECASE)==None, inputList))
    return list(filter(lambda x:(abs(matchSize-int(x["data"]["size"]))/matchSize)<=threshold,season))
def matchBySizeEpisodes(inputList,matchSize,threshold):
    threshold=threshold/100
    episodes=list(filter(lambda x: re.search("E[0-9][0-9]+",x["sourceTitle"],re.IGNORECASE), inputList))
    episodeSize=list(map(lambda x:int(x["data"]["size"]),episodes))
    if (abs(matchSize-sum(episodeSize))/matchSize)<=threshold:
        return episodes
    return []
def matchDate(inputList, maxAge, currDate):
    return list(filter(lambda x: (currDate-arrow.get(x["publishDate"])).days <= maxAge, inputList))

   
def matchQuality(inputList, matchQuality):
    return list(filter(lambda x: guessit(x["sourceTitle"]).get("source")==matchQuality, inputList))


def matchVideo(inputList, res,vidCodec,vidProfile):
    filtered=inputList
    if res==None and vidCodec==None and vidProfile==None:
        return []
    if res:
        filtered= list(filter(lambda x: guessit(x["sourceTitle"]).get("screen_size") == res and 
        guessit(x["sourceTitle"]).get("screen_size")!=None, inputList))
    if vidCodec:
        filtered= list(filter(lambda x: guessit(x["sourceTitle"]).get("video_codec") == vidCodec and 
        guessit(x["sourceTitle"]).get("video_codec")!=None , filtered))
    if vidProfile:
        filtered= list(filter(lambda x: guessit(x["sourceTitle"]).get("video_profile") == vidProfile and
        guessit(x["sourceTitle"]).get("video_profile")!=None, filtered))
    return filtered

def matchSpecial(inputList,matchTitle):
    if re.search("proper",matchTitle,re.IGNORECASE):
        return list(filter(lambda x: re.search("proper", x["sourceTitle"],re.IGNORECASE), inputList))
    
    elif re.search("repack", matchTitle, re.IGNORECASE):
        return list(filter(lambda x: re.search("repack", x["sourceTitle"], re.IGNORECASE), inputList))
    return inputList

def matchSeasonNum(inputList,matchSeason):
    return list(filter(lambda x:guessit(x["title"]).get("season")==matchSeason,inputList))
 







def matchByTitle(inputList,matchGroup,matchTitle):
    matches=[]
    matchTitle=titleCleanUp(matchTitle)
    for ele in inputList:
        titlePercent=.95
        eleGroup = ele["data"].get("releaseGroup")or guessit(ele["sourceTitle"]).get("release_group", "")
        eleTitle=ele["sourceTitle"]
        eleTitle=titleCleanUp(eleTitle)
        if len(matchGroup)>0 and len(eleGroup)>0:
            if jellyfish.jaro_distance(matchGroup.lower(), eleGroup.lower()) >= .95:
                titlePercent=.90
        # if jellyfish.jaro_distance(matchTitle, eleTitle.lower()) <titlePercent:
        #     continue
        matches.append(ele)
       
    return matches

def titleCleanUp(title):
    title=re.sub(" +","",title)
    title=re.sub("\[","",title)
    title=re.sub("\]","",title)
    title=re.sub("\+","",title)
    title=re.sub("\*","",title)
    title=re.sub("[.-]","",title)
    title=title.lower()
    return title

        


