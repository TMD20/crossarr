
import datetime
import os

import re
import tempfile
import shutil



from pyarr import RadarrAPI

from guessit import guessit

import arr.filter as radarrFilter
from arr.base import Base
import console


class Radarr(Base):
    def __init__(self):
        super().__init__()
        self.url = self.args.radarr.url
        self.api = self.args.radarr.api
        self.folder = self.args.radarr.folder
        self.radarr = RadarrAPI(self.url, self.api)
       
  
     
###################################################################
#Process Functions
#####################################################################

    def _findCrossSeeds(self):
        with self.live:
            movies=self._getMovies()
            self.overallProgress.update(self.mediaTask,total=len(movies))
            for movie in movies:
                self.overallProgress.update(self.mediaTask,description=f"Overall Media Progress: {movie['title']}")
                self._matchMovie(movie)
                self.overallProgress.update(self.mediaTask,description=f"Overall Media Progress: ",advance=1)

    
    def _matchMovie(self, movie):
        downloadList = self._getDownloads(movie)
        downloadList=list(map(lambda x:self._normalizeObj(x),downloadList))
        releasesList = self._getReleases(f"{movie['title']} {movie['year']}")
        self.overallProgress.update(self.releaseTask,description=f"",total=len(downloadList))
        for ele in downloadList:
            self.overallProgress.update(self.releaseTask,description=f"{movie['title']} Progress: Looking for matching releases for {ele['title']}")
            matchingReleases=self._verifyMatches(releasesList,ele)
            for release in matchingReleases:
                self._downloadItem(release)
            self.overallProgress.update(self.releaseTask,description=f"Current Movie Progress: ",advance=1)

      
  
    def _verifyMatches(self,releasesList,prevDownload):
        title=prevDownload["title"]
        size=int(prevDownload["size"])
        prevDownloadInfo=guessit(title)
        releaseGroup = prevDownloadInfo.get("release_group")
        resolution = prevDownloadInfo.get("screen_size")
        quality=prevDownloadInfo.get("source")
        resolution = prevDownloadInfo.get("screen_size")
        videoCodec = prevDownloadInfo.get("video_codec")
        videoProfile = prevDownloadInfo.get("video_profile")
       
    
        filtered = radarrFilter.matchByTitle(releasesList, releaseGroup,title)
        filtered = radarrFilter.matchQuality(filtered,quality)
        filtered = radarrFilter.matchVideo(filtered, resolution,videoCodec,videoProfile)
        filtered = radarrFilter.matchSpecial(filtered, title) 
        filtered=radarrFilter.matchBySize(filtered,size,self.threshold)
        return filtered  

    ###################################################################
    #Process Helpers
    #####################################################################
    
    def _setArrDataNormalizers(self):
        super()._setArrDataNormalizers()
        self.arrID=lambda x:x["movieId"]
        self.arrLang=lambda x:x["languages"][0]["name"] 

        
    ############################################################################
    #
    #  Data Retrivers
    ##############################################################################

    def _getMovies(self):
        self.movieList = self.radarr.get_movie() or []
        return self.movieList


    def _getDownloads(self, movie):
        downloadList=None
        if self.flag == "grabbed":
            downloadList = self._getGrabs(movie)
        elif self.flag == "imported":
            downloadList = self._getImported(movie)
        [ele["sourceTitle"]==self._titleSimplify(ele["sourceTitle"]) for ele in downloadList]
        return downloadList

    def _getGrabs(self, movie):
        grabHistory=self.radarr.get_movie_history(movie.get("id"), event_type="grabbed")
        uniqueTitles=set(list(map(lambda x:x["sourceTitle"],grabHistory)))
        temp=[]
        for ele in grabHistory:
            if ele["sourceTitle"] in uniqueTitles:
                temp.append(ele)
                uniqueTitles.remove(ele["sourceTitle"])
        return temp


    def _getImported(self, movie):
        grabHistory=self._getGrabs(movie)
        importHistory = self.radarr.get_movie_history(movie.get("id"), event_type="downloadFolderImported")
        deletedHistory = self.radarr.get_movie_history(movie.get("id"), event_type="movieFileDeleted")
        titleSet=set(list(map(lambda x:x["sourceTitle"],importHistory))+list(map(lambda x:x["sourceTitle"],deletedHistory)))
        return list(filter(lambda x:x["sourceTitle"] in titleSet,grabHistory))


        
    def _getReleases(self, title):
     
        query=f"{title}"
        url=f"{self.args.prowlarrurl}/api/v1/search"
        params={"apikey":self.args.prowlarrapi,"indexerIDs":self.indexerIDs,"query":query,"limit":1000,"categories":"2000","type":"movie"}
        req=self.session.get(url,params=params)
        if req.status_code!=200:
            self._rowHelper()
            msg=f"Req to {req.url} was not successful with status code {req.status_code}"
            self.messageTable.add_row("Error",msg,style="red")
            console.logging.error(msg)
            self.errorReq=self.errorReq+1
            return []
        else:
            self._rowHelper()
            msg=f"Req to {req.url} was successful with status code {req.status_code}"
            self.messageTable.add_row("Request",msg,style="green")
            console.logging.info(msg)
            self.successReq=self.successReq+1
        data=req.json()
        data=radarrFilter.matchDate(data,self.days,self.currDate)        
        return data



    def _setProgressBars(self):
        super()._setProgressBars()
        self.mediaTask=self.overallProgress.add_task(f"Overall Media Progress: ")
        self.releaseTask=self.overallProgress.add_task(f"Current Movie Progress:")
    