import datetime
import os
import re

import arrow
import requests_cache
import urllib3
session = requests_cache.CachedSession(
    'request.cache',expire_after=datetime.timedelta(days=1))


import setup.args as args
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
        self.dryrun=None
    
        



###################################################################
#Process Functions
#####################################################################
    
    def process(self,dryrun=False):
        self._getIndexerIDs()
        self._setConsole()
        self._setArrDataNormalizers()
        self._findCrossSeeds()
        self._finalOutPut()
    def _findCrossSeeds(self):
        None
    def _finalOutPut(self):      
        console.Console().print(f"\n\nFinal Statistics",style="deep_pink4")
        msg= \
        f"""
        Succesful Downloads: {self.download}
        Failed Downloads: {self.downloadFails}
        Successful Request: {self.successReq}
        Failed Request: {self.errorReq}
        """
        console.Console().print(msg,style="bold")
        console.logging.info(msg)
     

        

       

    
###################################################################
#Process Helpers
#####################################################################
    


    def _downloadItem(self,release):
        self._rowHelper()
        basename = f"[{release['indexer']}] {release['title']}.torrent"
        basename=self.titleFixer(basename)
        finalURL=release["downloadUrl"]
        data = session.get(finalURL)
        if self.dryrun:
            msg=f"Dry Run: [{release['indexer']}] {release['title']}.torrent"
            self.messageTable.add_row("Download",msg,style="green")
            console.logging.info(msg)
        elif data.status_code!=200:
            msg=f"Request to {finalURL} was not succesful with status code {data.status_code}"
            self.messageTable.add_row("Error",msg,style="red")
            console.logging.error(msg)
            self.downloadFails=self.downloadFails+1
        else:
            try: 
                savePath=os.path.join(self.folder,basename)
                with open(savePath,"wb") as file:
                        file.write(data.content)  
                msg=f"Saved Download to -> {savePath}"
                self.messageTable.add_row("Download",msg,style="green")
                console.logging.info(msg)
                self.download=self.download+1
            except:
                msg=f"Could not Saved Download to -> {savePath}"
                self.messageTable.add_row("Error",msg,style="RED")
                console.logging.error(msg)
                self.downloadFails=self.downloadFails+1
      
       


      

    def _titleSimplify(self,title):
        title=os.path.basename(title)
        title=os.path.splitext(title)[0]
        return title
    
    def titleFixer(self,title):
        title=re.sub("/","_",title)
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
        self.downloadFails=0

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