import re
import jellyfish
from guessit import guessit
import arrow





def matchDate(inputList,maxAge,currDate):
    return list(filter(lambda x:matchDateHelper(x,currDate,maxAge),inputList))
def matchDateHelper(input,currDate,maxAge):
    dateString=input.get("date") or input.get("publishDate")
    itemDate=arrow.get(dateString) 
    return (currDate-itemDate).days<=maxAge

def matchBySize(inputList,matchSize,threshold):
    threshold=threshold/100
    return list(filter(lambda x:(abs(matchSize-int(x["size"]))/matchSize)<=threshold,inputList))

def matchBySizeSeason(inputList,matchSize,threshold):
    threshold=threshold/100
    season=list(filter(lambda x: re.search("E[0-9][0-9]+",x["title"],re.IGNORECASE)==None, inputList))
    return list(filter(lambda x:(abs(matchSize-int(x["size"]))/matchSize)<=threshold,season))
def matchBySizeEpisodes(inputList,matchSize,threshold):
    threshold=threshold/100
    episodes=list(filter(lambda x: re.search("E[0-9][0-9]+",x["title"],re.IGNORECASE), inputList))
    episodeSize=list(map(lambda x:int(x["size"]),episodes))
    if (abs(matchSize-sum(episodeSize))/matchSize)<=threshold:
        return episodes
    return []        

def matchByTitle(inputList,matchGroup,matchTitle):
    matches=[]
    matchTitle=titleCleanUp(matchTitle)
    for ele in inputList:
        eleTitle=ele["title"]
        eleGroup = ele.get("releaseGroup") or guessit(eleTitle).get("release_group")
        eleTitle=titleCleanUp(eleTitle)
        if matchGroup and eleGroup:
            if jellyfish.jaro_distance(matchGroup.lower(), eleGroup.lower()) < .95:
                continue
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


def matchQuality(inputList, matchQuality):
    return list(filter(lambda x: guessit(x["title"]).get("source")==matchQuality, inputList))

def matchVideo(inputList, res,vidCodec,vidProfile):
    filtered=inputList
    if res==None and vidCodec==None and vidProfile==None:
        return []
    if res:
        filtered= list(filter(lambda x: guessit(x["title"]).get("screen_size") == res and 
        guessit(x["title"]).get("screen_size")!=None, inputList))
    if vidCodec:
        filtered= list(filter(lambda x: guessit(x["title"]).get("video_codec") == vidCodec and 
        guessit(x["title"]).get("video_codec")!=None , filtered))
    if vidProfile:
        filtered= list(filter(lambda x: guessit(x["title"]).get("video_profile") == vidProfile and
        guessit(x["title"]).get("video_profile")!=None, filtered))
    return filtered
  
def matchSpecial(inputList,matchTitle):
    if re.search("proper",matchTitle,re.IGNORECASE):
        return list(filter(lambda x: re.search("proper", x["title"],re.IGNORECASE), inputList))
    elif re.search("repack", matchTitle, re.IGNORECASE):
        return list(filter(lambda x: re.search("repack", x["title"], re.IGNORECASE), inputList))
    return inputList   

def matchSeasonNum(inputList,matchSeason):
    return list(filter(lambda x:guessit(x["title"]).get("season")==matchSeason,inputList))
 




