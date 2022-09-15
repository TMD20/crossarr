
import datetime
import string
import os
import urllib.parse
import re
import itertools



import arrow
from pyarr import RadarrAPI
import requests_cache
session = requests_cache.CachedSession(
    'request.cache',expire_after=datetime.timedelta(days=1))
from guessit import guessit

import radarr.filter as radarrFilter
import console

import args
args = args.getArgs()

class Radarr():
    def __init__(self):
        self.url = args.radarr.url
        self.api = args.radarr.api
        self.userindexers = args.indexers
        self.flag = args.flag
        self.folder = args.radarr.folder
        self.days = args.days
        self.radarr = RadarrAPI(self.url, self.api)
        self.threshold = args.threshold
        self.currDate = arrow.get()
        self.progress= console.Progress()
        self.downloadTask=console.Status("Save Download to -> Nothing Downloaded Yet ")
        self.movieTask=self.progress.add_task(f"")
        self.releaseTask=self.progress.add_task(f"")
        self.renderGroup=console.Group(self.progress,self.downloadTask)
        

    def Process(self):
        self.getIndexerIDs()
        with console.Live(self.renderGroup) as live:
            movies=self.getMovies()
            self.progress.update(self.movieTask,total=len(movies))
            for movie in movies:
                self.progress.update(self.movieTask,advance=1,description=f"Searching for a matching releases: {movie['title']}")
                self.findCross_Seed(movie)
    
    def printMatchData(self,match,element):
        print(match["data"]["size"],element["size"])
        print(match["sourceTitle"], element["title"])
        print("\n\n")

      
  
    def downloadItem(self,release):
        basename = f"[{release['indexer']}] {release['title']}.torrent"
        urlParts=urllib.parse.urlparse(release["downloadUrl"])
        # radarr may use a different url, then running machine
        url=self.url
        for i in range(2,len(urlParts)):
            url=urllib.parse.urljoin(url,urlParts[i])

        savePath = os.path.join(self.folder, basename)
        data = session.get(url)

        # Save file data to local copy
        with open(savePath,"wb") as file:
            file.write(data.content)
        self.downloadTask.update(f"Saved Download to -> {savePath}")



        


    def getMovies(self):
        self.movieList = self.radarr.get_movie() or []
        return self.movieList

    def getIndexerIDs(self):
        indexerURL=f"{args.prowlarrurl}/api/v1/indexer"
        indexerIDs = []
        indexerNames = []
        req=session.get(indexerURL,params={"apikey":args.prowlarrapi})
        allIndexer=req.json()
        for indexer in allIndexer:
            for ele in self.userindexers:
                if re.search(ele, indexer["name"], re.IGNORECASE):
                    indexerIDs.append(indexer["id"])
                    indexerNames.append(indexer["name"])
        self.indexerIDs= list(set(indexerIDs))
        self.indexerNames = list(set(indexerNames))
    def titleHelper(self,title):
        title=os.path.basename(title)
        title=os.path.splitext(title)[0]
        return title
      
    def findCross_Seed(self, movie):
        downloadList = self.getDownloads(movie)
        releasesList = self.getReleases(f"{movie['title']} {movie['year']}")
        self.progress.update(self.releaseTask,description=f"",total=len(downloadList))
        for ele in downloadList:
            self.progress.update(self.releaseTask,description=f"Checking if {ele['sourceTitle']} has a matching release",advance=1)
            matchingReleases=self.findMatches(releasesList,ele)
            for release in matchingReleases:
                self.downloadItem(release)
    def findMatches(self,releasesList,ele):
        title=ele["sourceTitle"]
        size=int(ele["data"]["size"])


        eleInfo=guessit(title)
        releaseGroup = eleInfo.get("release_group","")
        resolution = eleInfo.get("screen_size")
        quality=eleInfo.get("source")
        resolution = eleInfo.get("screen_size")
        videoCodec = eleInfo.get("video_codec")
        videoProfile = eleInfo.get("video_profile")
       
     
     
        filtered = radarrFilter.matchByTitle(releasesList, releaseGroup,title)
        filtered = radarrFilter.matchQuality(filtered,quality)
        filtered = radarrFilter.matchVideo(filtered, resolution,videoCodec,videoProfile)
        filtered = radarrFilter.matchSpecial(filtered, title) 
        filtered=radarrFilter.matchBySize(filtered,size,self.threshold)
        return filtered      
            

    def getDownloads(self, movie):
        downloadList=None
        if self.flag == "grabbed":
            downloadList = self.getGrabs(movie)
        elif self.flag == "imported":
            downloadList = self.getImported(movie)
        [ele["sourceTitle"]==self.titleHelper(ele["sourceTitle"]) for ele in downloadList]
        return downloadList

    def getGrabs(self, movie):
        return self.radarr.get_movie_history(movie.get("id"), event_type="grabbed")


    def getImported(self, movie):
        grabHistory=self.getGrabs(movie)
        importHistory = self.radarr.get_movie_history(movie.get("id"), event_type="downloadFolderImported")
        deletedHistory = self.radarr.get_movie_history(movie.get("id"), event_type="movieFileDeleted")
        titleSet=set(list(map(lambda x:x["sourceTitle"],importHistory))+list(map(lambda x:x["sourceTitle"],deletedHistory)))
        return list(filter(lambda x:x["sourceTitle"] in titleSet,grabHistory))


        
    def getLargest(self, movie):
        grabs = self.getGrabs(movie)
        if len(grabs) == 0:
            return grabs
        return list(sorted(grabs, key=lambda x: x["data"]["size"], reverse=True))[0]

    def getSmallest(self, movie):
        grabs = self.getGrabs(movie)
        if len(grabs) == 0:
            return grabs
        return list(sorted(grabs, key=lambda x: x["data"]["size"]))[0]

    def getOldest(self, movie):
        grabs = self.getGrabs(movie)
        if len(grabs) == 0:
            return grabs
        return list(sorted(grabs, key=lambda x: datetime.datetime.strptime(x["date"], self.dateString)))[0]

    def getNewest(self, movie):
        grabs = self.getGrabs(movie)
        if len(grabs) == 0:
            return grabs
        return list(sorted(grabs, key=lambda x: datetime.datetime.strptime(x["date"], self.dateString), reverse=True))[0]

    def getReleases(self, title):
     
        query=f"{title}"
        url=f"{args.prowlarrurl}/api/v1/search"
        params={"apikey":args.prowlarrapi,"indexerIDs":self.indexerIDs,"query":query,"limit":1000,"categories":"2000","type":"movie"}
        req=session.get(url,params=params)
        if req.status_code!=200:
            return []
        data=req.json()
        data=radarrFilter.matchDate(data,self.days,self.currDate)        
        return data
