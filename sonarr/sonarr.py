import args
import datetime
import string
import re
import itertools
import os
import urllib.parse

from pyarr import SonarrAPI
import arrow
from guessit import guessit

import sonarr.filter as sonarrFilter
import console


import requests_cache
session = requests_cache.CachedSession(
    'request.cache', expire_after=datetime.timedelta(days=1))


args = args.getArgs()


class Sonarr():
    def __init__(self):
        self.url = args.sonarr.url
        self.api = args.sonarr.api
        self.userindexers = args.indexers
        self.flag = args.flag
        self.folder = args.sonarr.folder
        self.days = args.days
        self.sonarr = SonarrAPI(self.url, self.api)
        self.threshold = args.threshold
        self.prowlarrurl=args.prowlarrurl
        self.prowlarrapi=args.prowlarrapi
        self.currDate = arrow.get()
        self.progress= console.Progress()
        self.downloadTask=console.Status("Save Download to -> Nothing Downloaded Yet ")
        self.showTask=self.progress.add_task(f"")
        self.seasonTask=self.progress.add_task(f"")
        self.releaseTask=self.progress.add_task(f"")
        self.renderGroup=console.Group(self.progress,self.downloadTask)
        
       


       
    

 

  
    def getShows(self):
        self.series=self.sonarr.get_series()
        return self.series


    def Process(self):
        self.getIndexerID()
        shows=self.getShows()
        with console.Live(self.renderGroup) as live:
            self.progress.update(self.showTask,description=f"",advance=1,total=len(shows))
            for show in shows:
                self.progress.update(self.showTask,description=f"Searching for a matching releases: {show['title']}",advance=1)
                self.ProcessShow(show)
      

    def getFullSeasonReleases(self,num,show):
        query=f"{{Season:{num}}} {show}"
        url=f"{self.prowlarrurl}/api/v1/search"
        params={"apikey":self.prowlarrapi,"indexerIDs":self.indexerIDs,"query":query,"limit":1000,"categories":"5000","type":"tvsearch"}
        req=session.get(url,params=params)
        if req.status_code!=200:
            return []
        data=req.json()
        data=sonarrFilter.matchSeasonNum(data,num)
        data=sonarrFilter.matchDate(data,self.days,self.currDate)
   
        
        return data
       

    def findMatchinHistory(self, release, seasonHistory,epCount): 
        title=release["title"]
        size=int(release["size"])
        releaseData=guessit(title,"")
        releaseGroup = releaseData.get("release_group","")
        resolution = releaseData.get("screen_size")
        quality=releaseData.get("source")
        resolution = releaseData.get("screen_size")
        videoCodec = releaseData.get("video_codec")
        videoProfile = releaseData.get("video_profile")
       
        
        filtered = sonarrFilter.matchByTitle(seasonHistory, releaseGroup,title)
        filtered = sonarrFilter.matchQuality(filtered,quality)
        filtered = sonarrFilter.matchVideo(filtered, resolution,videoCodec,videoProfile)
        filtered = sonarrFilter.matchSpecial(filtered, title)
        filteredSeason=sonarrFilter.matchBySizeSeason(filtered,size,self.threshold)
        filteredEpisode=sonarrFilter.matchBySizeEpisodes(filtered,size,self.threshold)
        if (len(max([filteredEpisode,filteredSeason],key=lambda x:len(x)))/epCount)>.7:
                return True

    
  
    
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

       




  

        


            

              






    def ProcessShow(self,show):
        id=show["id"]
        showTitle=show["title"]
        i=1
        self.progress.update(self.seasonTask,description=f"",total=len(show["seasons"])-1,completed=0)
    
        while i<len(show["seasons"]):
            season = show["seasons"][i]
            self.progress.update(self.seasonTask,description=f"Look at season Number:{season['seasonNumber']}",style=console.normal_header_style,advance=1)
            i=i+1
            epCount = season["statistics"]["totalEpisodeCount"]
            num = season["seasonNumber"]
            downloadHistory=self.getDownloadHistory(num,id)
            if len(downloadHistory)==0:
                continue
            releases=self.getFullSeasonReleases(num,showTitle)
            if len(releases)==0:
                continue
            self.progress.update(self.releaseTask,description=f"",total=len(releases),completed=0)
            for release in releases:
                self.progress.update(self.releaseTask,description=f"Checking if {release['title']} was previously Downloaded",advance=1)
                if not self.findMatchinHistory(release,downloadHistory,epCount):
                    continue
                self.downloadItem(release)
            


    
    def titleHelper(self,title):
        title=os.path.basename(title)
        title=os.path.splitext(title)[0]
        return title
    
    
    def getDownloadHistory(self,seasonNum,id): 
        url=f"{self.url}/api/v3/history/series" 
        req=session.get(url,params={"seasonNumber":seasonNum,"apikey":self.api,"seriesid":id})    
        data=req.json() 
        [ele["sourceTitle"]==self.titleHelper(ele["sourceTitle"]) for ele in data]
        return self.downloadHistoryFilter(data)
    def downloadHistoryFilter(self,downloadHistory):
        grabHistory=list(filter(lambda x:x["eventType"]=="grabbed",downloadHistory))
        uniqueTitles=set(list(map(lambda x:x["sourceTitle"],grabHistory)))
        temp=[]
        for ele in grabHistory:
            if ele["sourceTitle"] in uniqueTitles:
                temp.append(ele)
                uniqueTitles.remove(ele["sourceTitle"])
        if self.flag=="grabbed":
            return grabHistory
        importHistory=list(filter(lambda x:x["eventType"]=="downloadFolderImported",downloadHistory))
        deletedHistory=list(filter(lambda x:x["eventType"]=="episodeFileDeleted",downloadHistory))
        titleSet=set(list(map(lambda x:x["sourceTitle"],importHistory))+list(map(lambda x:x["sourceTitle"],deletedHistory)))

        return list(filter(lambda x:x["title"] in titleSet,grabHistory))


           
        

        
            
            

            

    def getIndexerID(self):
        indexerURL=f"{self.prowlarrurl}/api/v1/indexer"


        indexerIDs = []
        indexerNames = []
        req=session.get(indexerURL,params={"apikey":self.prowlarrapi})
        allIndexer=req.json()
        for indexer in allIndexer:
            for ele in self.userindexers:
                if re.search(ele, indexer["name"], re.IGNORECASE):
                    indexerIDs.append(indexer["id"])
                    indexerNames.append(indexer["name"])
        self.indexerIDs= list(set(indexerIDs))
        self.indexerNames = list(set(indexerNames))
      

    