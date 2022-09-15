import re
import jellyfish
import datetime
from guessit import guessit
import arrow




def matchDate(inputList,maxAge,currDate):
    # return list(filter(lambda x: (currDate-(arrow.get(x.get("publishDate"))or arrow.get(x.get("date") )).days <= maxAge, inputList)))
    return list(filter(lambda x:matchDateHelper(x,currDate,maxAge),inputList))
def matchDateHelper(input,currDate,maxAge):
    dateString=input.get("publishDate") or input.get("date")
    itemDate=arrow.get(dateString) 
    return (currDate-itemDate).days<=maxAge

def matchBySize(inputList,matchSize,threshold):
    threshold=threshold/100
    return list(filter(lambda x:(abs(matchSize-int(x["size"]))/matchSize)<=threshold,inputList))
        

def matchByTitle(inputList,matchGroup,matchTitle):
    matches=[]
    matchTitle=titleCleanUp(matchTitle)
    for ele in inputList:
        titlePercent=.95
        eleGroup=ele.get("releaseGroup") or guessit(ele["title"]).get("release_group", "")
        eleTitle=ele["title"]
        eleTitle=titleCleanUp(eleTitle)

        if len(matchGroup)>0 and len(eleGroup)>0:
            if jellyfish.jaro_distance(matchGroup.lower(), eleGroup.lower()) >= .95:
                titlePercent=.90
        if jellyfish.jaro_distance(matchTitle, eleTitle.lower()) >= titlePercent:
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




