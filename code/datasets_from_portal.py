import pandas as pd
import sodapy
import structlog

from sodapy import Socrata
from portal import Portal
from urllib.parse import urlparse,urljoin

import time
import requests

from pprint import pformat

class Model(object):

    def __init__(self, **kwargs):
        self.__hash= hash(pformat(kwargs))

    def __eq__(self, other):
        if isinstance(other, Model):
            return (self.__hash == other.__hash )
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self, *args, **kwargs):
        return self.__hash

class Dataset_data(Model):

    def __init__(self, portalID, did, **kwargs):
        super(Dataset_data,self).__init__(**{'city':portalID,'id':did})

        self.id = did
        self.city = portalID
        self.name = None
        self.uri = None
        self.viewCount = None
        self.downloadCount = None
        self.category = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def dataset_dict(self):
        d=dict()
        d.update({'id':self.id,
                         'city':self.city,
                         'name':self.name,
                         'uri':self.uri,
                         'viewCount':self.viewCount,
                         'downloadCount':self.downloadCount,
                         'category':self.category})
        return d

def getPortalProcessor(P):
    if P.platform == 'Socrata':  ### AQ 28/07/2019
        return Socrata()
    else:
        raise NotImplementedError(P.software + ' is not implemented')


class PortalProcessor:
    def generateFetchDatasetIter(self, Portal, PortalSnapshot, sn):
        raise NotImplementedError("Should have implemented this")



class Socrata(PortalProcessor):
    def generateFetchDatasetIter(self, Portal):

        log = structlog.get_logger()

        # Mod 12102023
        # if Portal.software=='Socrata':
        if 'Socrata' in Portal.platform:
            # End Mod. 12102023
            api = urljoin(Portal.url, '/api')
            # api=Portal.apiuri
            page = 1
        else:
            ### api = Portal.id + Portal.apiuri
            offset = 1
            limit = 200

        processed = set([])

        while True:
            # Mod 12102023
            # if Portal.software=='Socrata':
            if 'Socrata' in Portal.platform:
                # End Mod. 12102023
                url = api + '/views?page=' + str(page)
                # print
                # url
                resp = requests.get(url, verify=False)
                # resp = requests.get(urlparse.urljoin(api, '/views?page=' + str(page)), verify=False)
            else:
                # resp = requests.get(urlparse.urljoin(api, '&offset=' + str(offset))+"&limit="+str(limit), verify=False)
                url = api + '&offset=' + str(offset) + "&limit=" + str(limit)
                resp = requests.get(url, verify=False)
                # resp = requests.get(urlparse.urljoin(api, '&offset=' + str(offset)+"&limit="+str(limit)), verify=False)

            if resp.status_code != requests.codes.ok:
                # TODO wait? appropriate message
                pass

            res = None

            if Portal.platform == 'Socrata':
                res = resp.json()
            else:
                try:
                    res = resp.json()['results']
                except:
                    print
                    Portal.url
            # returns a list of datasets
            if not res:
                break
            for datasetJSON in res:
                if Portal.platform == 'Socrata':
                    if 'id' not in datasetJSON:
                        continue
                    datasetID = datasetJSON['id']

                else:
                    if 'id' not in datasetJSON['resource']:
                        continue
                    datasetID = datasetJSON['resource']['id']

                d_id=datasetID
                d_city=Portal.city
                d_name=datasetJSON['name']
                d_uri=urljoin(api,'dataset/'+datasetID)
                if 'viewCount' in datasetJSON:
                    d_viewCount=datasetJSON['viewCount']
                else:
                    d_viewCount=0
                if 'downloadCount' in datasetJSON:
                    d_downloadCount=datasetJSON['downloadCount']
                else:
                    d_downloadCount=0
                if 'category' in datasetJSON:
                    d_category=datasetJSON['category']
                else:
                    d_category='Unspecified'

                d=Dataset_data(portalID=d_city,did=d_id,name=d_name,uri=d_uri,viewCount=d_viewCount,downloadCount=d_downloadCount,category=d_category)

                if datasetID not in processed:
                    processed.add(datasetID)
                    if Portal.platform == 'Socrata':
                        pid = Portal.city
                    else:
                        pid = Portal.apiuri.split("=")[1]

                    if len(processed) % 1000 == 0:
                        log.info("ProgressDSFetch", pid=Portal.city, processed=len(processed))
                    yield d

            if Portal.platform == 'Socrata':
                page += 1
            else:
                offset = offset + limit

#####
def getPortalDatasets(Portal):
    ###
    ###     Returns list of extracted datasets from Portal (Dataset_data type objects)
    ###
    start = time.time()
    datasets = []
    processor = getPortalProcessor(Portal)
    for d in processor.generateFetchDatasetIter(Portal):
        datasets.append(d.dataset_dict())

    print('total downloaded datasets:', len(datasets))
    end = time.time()
    print('exec time:', end - start)

    return datasets


def portals_ETL(portals,output_filename,get,load,usage,quality):

    import json
    import os
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    allPortalsDatasetsFile = output_dir + output_filename

    file = open(allPortalsDatasetsFile, 'w', encoding="utf-8")

    with file as json_file:
        datasets=[]
        for p in portals:
            portal = Portal()
            portal.city = p[1]
            portal.url = p[0]
            portal.platform = p[3]

            if get:
                print("============================= D O W N L O A D ================================")
                start = time.time()
                datasets.append(getPortalDatasets(portal))
                end = time.time()
                print ('Downloading time for portal: '+portal.city+'  ('+str(int(end - start))+'   sec)')

        datasets=sum(datasets, [])
        s = json.dumps(datasets,
                       indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
        file.writelines(s)
    file.close()


if __name__ == '__main__':

    portalsUS= [
            ["https://data.austintexas.gov", 'Austin', '2019-12-19', 'Socrata', '2353', '875463'],  # API ok
            ["https://data.cityofnewyork.us",'New York','2019-12-19','Socrata','2771','8272963'],   #API ok
            ["https://data.buffalony.gov",'Buffalo','2019-12-19','Socrata','213','260041'],         #API ok
            ["https://data.cityofchicago.org",'Chicago','2019-12-19','Socrata','1368','2726772'],   #API ok
            ["https://data.lacity.org",'Los Angeles','2019-12-18','Socrata','943','3883916'],       #API ok
            ["https://data.seattle.gov",'Seattle','2019-12-19','Socrata','718','654224'],           #API ok
            ['https://data.sfgov.org','San Francisco','2019-12-19','Socrata','1001','839841'],      #API ok
            ["https://www.dallasopendata.com",'Dallas','2019-12-19','Socrata','1001','1259239'],    #API ok
            ["https://data.honolulu.gov",'Honolulu','2019-12-19','Socrata','244','349275'],         #API ok
            ['https://data.providenceri.gov','Providence','2019-12-19','Socrata','288','178784'],   #API ok
            ['https://data.nola.gov','New Orleans','2019-12-19','Socrata','215','378623'],          #API ok
            ["https://data.nashville.gov",'Nashville','2019-12-19','Socrata','172','636267'],       #API ok  #Ricaricare i datasetss
         ]

    portals = [["https://data.mesaaz.gov", 'Mesa', '', 'Socrata', '1160', ''],  # API ok
                ['https://data.oaklandca.gov', 'Oakland', '', 'Socrata', '819', ''],  # API ok
                ["https://stat.stpete.org", 'St. Petersburg', '', 'Socrata', '628', ''], ]

    get=True;
    load=False;
    usage=False;
    quality=False;
    portals=portals

    output_filename="3PortalsDatasetsFile.json"
    ###  get data from portals
    portals_ETL(portals,output_filename,get,load,usage,quality)  ###(A T T E N T I O N: rewriting 'output_filename')

