import datetime
import os
import re

import arrow
import requests_cache
import urllib3
session = requests_cache.CachedSession(
    'request.cache',expire_after=datetime.timedelta(days=1))


import args
import console

class Base():
    def __init__(self):
        self.args=args.getArgs()
        self.currDate = arrow.get()
        self.threshold = self.args.threshold
        self.days = self.args.days
        self.userindexers = self.args.indexers
        self.flag = self.args.flag
        self.session=session
        self.prowlarrurl=self.args.prowlarrurl
        self.prowlarrapi=self.args.prowlarrapi
    
        



###################################################################
#Process Functions
#####################################################################
    
    def process(self):
        self._getIndexerIDs()
        self._setConsole()
        self._setArrDataNormalizers()
        self._findCrossSeeds()
        self._finalOutPut()
    def _findCrossSeeds(self):
        None
    def _finalOutPut(self):      
        console.Console().print(f"\n\nFinal Statistics",style="deep_pink4")
        console.Console().print(f"Total Downloads: {self.download}",style="bold")
        console.Console().print(f"Successful Request: {self.successReq}",style="bold")
        console.Console().print(f"Failed Request: {self.errorReq}",style="bold") 

        

       

    
###################################################################
#Process Helpers
#####################################################################
    


    def _downloadItem(self,release):
        # build urlback, just in case radarr is in a docker or does not have the same urlbase
        prowlarrURLParts=urllib3.util.parse_url(self.prowlarrurl)
        downloadURLParts=urllib3.util.parse_url(release["downloadUrl"])
        finalURL=urllib3.util.Url(prowlarrURLParts.scheme,prowlarrURLParts.auth,prowlarrURLParts.host,prowlarrURLParts.port,downloadURLParts.path,downloadURLParts.query).url

        basename = f"[{release['indexer']}] {release['title']}.torrent"

        data = session.get(finalURL)
        if data.status_code!=200:
            self.messageTable.add_row("Error",f"Request to {finalURL} was not succesful with status code {data.status_code}",style="red")
 

        savePath=os.path.join(self.folder,basename)
        with open(savePath,"wb") as file:
                file.write(data.content)
        self.download=self.download+1
        self._rowHelper()
        self.messageTable.add_row("Download",f"Saved Download to -> {savePath}",style="green")


      

    def _titleSimplify(self,title):
        title=os.path.basename(title)
        title=os.path.splitext(title)[0]
        return title



    
    
    def _getIndexerIDs(self):
        indexerURL=f"{self.prowlarrurl}/api/v1/indexer"


        indexerIDs = []
        indexerNames = []
        req=self.session.get(indexerURL,params={"apikey":self.prowlarrapi})
        allIndexer=req.json()
        for indexer in allIndexer:
            for ele in self.userindexers:
                if re.search(ele, indexer["name"], re.IGNORECASE):
                    indexerIDs.append(indexer["id"])
                    indexerNames.append(indexer["name"])
        self.indexerIDs= list(set(indexerIDs))
        self.indexerNames = list(set(indexerNames))


    def _setArrDataNormalizers(self):
        self.arrTitle=lambda x:x["sourceTitle"]
        self.arrID=lambda x:x["seriesId"]
        self.arrDate=lambda x:x["date"]
        self.arrEvent=lambda x:x["eventType"]
        self.arrQuality=lambda x:x["quality"]["quality"]["name"]
        self.arrGroup=lambda x:x["data"]["releaseGroup"]
        self.arrSize=lambda x:x["data"]["size"]
        self.arrLang=lambda x:x["language"][0]["name"] 

    

    def _normalizeObj(self,obj):
        out={}
        out["title"]=self.arrTitle(obj)
        out["id"]=self.arrID(obj)
        out["lang"]=self.arrLang(obj)
        out["date"]=self.arrDate(obj)
        out["eventType"]=self.arrEvent(obj)
        out["quality"]=self.arrQuality(obj)
        out["releaseGroup"]=self.arrGroup(obj)
        out["size"]=self.arrSize(obj)
        return out


###################################################################
#Message Functions
#####################################################################

    def _setConsole(self):
        self._setMessagesTable()
        self._setProgressBars()
        self.renderGroup=console.Group(self.messageTable,self.overallProgress)
        self.outputConsole=console.Console()
        self.live=console.Live(self.renderGroup,console=self.outputConsole)
        # counters for final message output
        self.successReq=0
        self.errorReq=0
        self.download=0

    def _setMessagesTable(self):
        #Message table
        self.messageTable=console.Table(title="Program Messages")
        self.messageTable.add_column("Name")
        self.messageTable.add_column("Message")
        self.maxTableRows=self.args.rows
        self.messageTable=console.Table()


    def _setProgressBars(self):
        self.overallProgress= console.Progress(console.TaskProgressColumn(),console.BarColumn(),console.TextColumn("{task.description}"))

    def _rowHelper(self):
        if len(self.messageTable.rows)==self.maxTableRows:
            self.messageTable=console.Table(title="Program Messages")
            self.messageTable.add_column("Name")
            self.messageTable.add_column("Message")
        self.renderGroup=console.Group(self.messageTable,self.overallProgress)
        self.live.update(self.renderGroup)