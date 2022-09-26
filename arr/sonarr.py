from pyarr import SonarrAPI
from guessit import guessit

import arr.filter as sonarrFilter
import console
from arr.base import Base





class Sonarr(Base):
    def __init__(self):
        super().__init__()

        self.url = self.args.sonarr.url
        self.api = self.args.sonarr.api
        self.folder = self.args.sonarr.folder
        self.sonarr = SonarrAPI(self.url, self.api)
      

      
    ############################################################################
    #
    # Process Functions
    ##############################################################################
      
        

    def _findCrossSeeds(self):
        '''
        processes the Cross-seeding request for user

                Parameters:
                        NONE

                Returns:
                        None
        '''
    
        shows=self._getShows()
        with self.live:
            self.overallProgress.update(self.mediaTask,description=f"Overall Media Progress:",total=len(shows))
            for show in shows:
                self.overallProgress.update(self.mediaTask,description=f"Overall Media Progress: Searching -> {show['title']}")
                self._processShow(show)
                self.overallProgress.update(self.mediaTask,advance=1)

               
    
    def _processShow(self,show):
        id=show["id"]
        showTitle=show["title"]
        i=1
        self.overallProgress.update(self.seasonTask,description=f"{show['title']} Progress: ",total=len(show["seasons"])-1,completed=0)
    
        while i<len(show["seasons"]):
            season = show["seasons"][i]
            for _ in range(1):
                self.overallProgress.update(self.seasonTask,description=f"{show['title']} Progress: Matching Releases for season num {season['seasonNumber']}",style=console.normal_header_style)
                epCount = season["statistics"]["totalEpisodeCount"]
                num = season["seasonNumber"]
                downloadHistory=self._getDownloadHistory(num,id)
                downloadHistory=list(map(lambda x:self._normalizeObj(x),downloadHistory))
                if len(downloadHistory)==0:
                    break
                releases=self._getFullSeasonReleases(num,showTitle)
                if len(releases)==0:
                    break
                self.overallProgress.update(self.releaseTask,description=f"",total=len(releases),completed=0)
                for release in releases:
                    self.overallProgress.update(self.releaseTask,description=f"{show['title']} Season {season['seasonNumber']} Releases Progress: Matching sonarr history to {release['title']}")
                    if not self._findMatchinHistory(release,downloadHistory,epCount):
                        self.overallProgress.update(self.releaseTask,advance=1)
                        continue
                self._downloadItem(release)
                self.overallProgress.update(self.releaseTask,advance=1)
  
            i=i+1
            self.overallProgress.update(self.releaseTask,description=f"Release Progress:",total=0)        
            self.overallProgress.update(self.seasonTask,description=f"{show['title']} Progress:",advance=1)
        self.overallProgress.update(self.seasonTask,description=f"Current Show Progress:",total=0)

            
    def _findMatchinHistory(self, release, seasonHistory,epCount): 
            title=release["title"]
            size=int(release["size"])
            releaseData=guessit(title,"")
            releaseGroup = releaseData.get("release_group")
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
   
    ############################################################################
    #
    # Process Helpers
    ##############################################################################
      
    def _setArrDataNormalizers(self):
        super()._setArrDataNormalizers()
        self.arrEP=lambda x:x["episodeId"]
        self.arrLang=lambda x:x["language"]["name"] 
 
    
    
    def _normalizeObj(self,obj):
        data=super()._normalizeObj(obj)
        data["episodeId"]=self.arrEP(obj)
        return data

    


   
    
    ############################################################################
    #
    #  Data Retrivers
    ##############################################################################
    def _getDownloadHistory(self,seasonNum,id): 
        url=f"{self.url}/api/v3/history/series" 
        req=self.session.get(url,params={"seasonNumber":seasonNum,"apikey":self.api,"seriesid":id})    
        data=req.json() 
        [ele["sourceTitle"]==self._titleSimplify(ele["sourceTitle"]) for ele in data]
        return self._downloadHistoryFilter(data)
        
    def _getShows(self):

        self.series=self.sonarr.get_series()
        return self.series
  
    
    def _getFullSeasonReleases(self,num,show):
        '''
        Retrives full season from prowlarr

            Parameters:
                    num()

            Returns:
                    None
        '''        
        query=f"{{Season:{num}}} {show}"
        url=f"{self.prowlarrurl}/api/v1/search"
        params={"apikey":self.prowlarrapi,"indexerIDs":self.indexerIDs,"query":query,"limit":1000,"categories":"5000","type":"tvsearch"}
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
        data=sonarrFilter.matchSeasonNum(data,num)
        data=sonarrFilter.matchDate(data,self.days,self.currDate)
   
        
        return data       
    ############################################################################
    #
    #  Data Modifiers
    ##############################################################################
    def _downloadHistoryFilter(self,downloadHistory):
        grabHistory=list(filter(lambda x:x["eventType"]=="grabbed",downloadHistory))
        uniqueTitles=set(list(map(lambda x:x["sourceTitle"],grabHistory)))
        temp=[]
        for ele in grabHistory:
            if ele["sourceTitle"] in uniqueTitles:
                temp.append(ele)
                uniqueTitles.remove(ele["sourceTitle"])
        grabHistory=temp
        if self.flag=="grabbed":
            return grabHistory

        
        importHistory=list(filter(lambda x:x["eventType"]=="downloadFolderImported",downloadHistory))
        deletedHistory=list(filter(lambda x:x["eventType"]=="episodeFileDeleted",downloadHistory))
        titleSet=set(list(map(lambda x:x["sourceTitle"],importHistory))+list(map(lambda x:x["sourceTitle"],deletedHistory)))

        return list(filter(lambda x:x["sourceTitle"] in titleSet,grabHistory))
    

       

  
    
    
    
    ############################################################################
    #
    #  Console
    ##############################################################################
    def _setProgressBars(self):
        super()._setProgressBars()
        self.mediaTask=self.overallProgress.add_task(f"Overall Media Progress: ")
        self.seasonTask=self.overallProgress.add_task(f"Current Show Progress:")
        self.releaseTask=self.overallProgress.add_task(f"Season Releases Progress:")
    
 

    