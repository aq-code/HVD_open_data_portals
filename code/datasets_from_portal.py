# -*- coding: utf8 -*-

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
def get_Portal_Datasets(Portal):
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


######################
def extract_Categories_Usage(portals, allPortalsDatasetsFile):

    from report import df_datasets_portals,extract_theme,write_portals_categories_usage,write_portals_stats

    listPortalsStats =[]
    listPortalsCategoryUsage = []

    all_datasets=df_datasets_portals(allPortalsDatasetsFile)

    for p in portals:
        portal = Portal()
        portal.city = p[1]
        portal.url = p[0]
        portal.platform = p[3]
        city =  str(p[1])

        catl = extract_theme(portal, all_datasets)
        catl = catl.sort_values(by='category')
        catl = catl.reset_index(drop=True)
        tot = catl['count'].sum()
        totv = catl['views'].sum()
        totd = catl['downl'].sum()
        catl['pdat'] = (catl['count'] / tot) * 100.0
        catl['pviews'] = (catl['views'] / totv) * 100.0
        catl['pdownl'] = (catl['downl'] / totd) * 100.0

        catl1 = extract_theme(portal, all_datasets, groupcat=False)

        stat = pd.DataFrame()
        stat['category'] = catl['category']
        stat['count'] = pd.to_numeric(catl["count"], downcast="integer")  # datasets number per category
        stat['pcount'] = stat['count'] / len(catl1)  # len(catl1) ->  datasets number per portal
        stat['views'] = catl['views']
        stat['pviews'] = catl['pviews']
        stat['downl'] = catl['downl']
        stat['pdownl'] = catl['pdownl']
        stat['mean'] = catl1.groupby(['category'])['downl'].mean().reset_index()['downl']

        perc=0.95
        if portal.platform == 'SocrataNew' or portal.platform == 'Socrata':
            stat['median'] = catl1.groupby(['category'])['downl'].median().reset_index()['downl']
            stat['p9X'] = catl1.groupby(['category'])['downl'].quantile(perc).reset_index()['downl']
        else:  ## Other portals
            stat['median'] = catl1.groupby(['category'])['views'].median().reset_index()['views']
            stat['p9X'] = catl1.groupby(['category'])['views'].quantile(perc).reset_index()['views']

        ###  HVDvalue metric
        stat['HVDvalue'] = stat['median'] * stat['pcount']+stat['p9X']*(stat['pcount']*(1-perc))

    #AQ begin 08042024 add save stat on dict, used by categories allignment and HDVi computation
        stat.set_index("category", drop=True, inplace=True)
        statdict = stat.to_dict(orient="index")
        dd = {'city': city, 'url':p[0], 'categorization':'Categories','platform':p[3], 'categories': statdict}
        listPortalsCategoryUsage.append(dd)

        dictStat={
            'City': city,
            'Datasets':     catl1['downl'].count(),
            'Downloads':    catl1['downl'].sum(),
            'Mean':         round(catl1['downl'].mean()),
            'Stdd':         round(catl1['downl'].std()),
            'Min':          round(catl1['downl'].min()),
            '1Q':           round(catl1['downl'].quantile(0.25)),
            '2Q':           round(catl1['downl'].quantile(0.5)),
            '3Q':           round(catl1['downl'].quantile(0.75)),
            'Max':          catl1['downl'].max()
        }
        listPortalsStats.append(dictStat)

    # AQ end 080424 add save stat on dict, used by categories allignment and HDVi computation
    write_portals_categories_usage(listPortalsCategoryUsage)

    statPortal = pd.DataFrame(listPortalsStats, columns=['City','Datasets','Downloads','Mean','Stdd','Min','1Q','2Q','3Q','Max'])
    write_portals_stats(statPortal)
    return listPortalsCategoryUsage

def portals_ETL(portals,output_filename,get=False,usage=False):

    import json
    import os
    output_dir = "output/"
    output_filename = "AllPortalsDatasetsFile.json"
    allPortalsDatasetsFile = output_dir + output_filename
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if get:
        file = open(allPortalsDatasetsFile, 'w', encoding="utf-8")
        with file as json_file:
            datasets=[]
            for p in portals:
                portal = Portal()
                portal.city = p[1]
                portal.url = p[0]
                portal.platform = p[3]
                print("============================= D O W N L O A D ================================")
                start = time.time()
                datasets.append(get_Portal_Datasets(portal))
                end = time.time()
                print ('Downloading time for portal: '+portal.city+'  ('+str(int(end - start))+'   sec)')
                print("===============================================================================")
            datasets=sum(datasets, [])
            s = json.dumps(datasets,
                           indent=4, ensure_ascii=False).encode('utf8').decode('latin1')
            file.writelines(s)
        file.close()
    if usage:
        extract_Categories_Usage(portals, allPortalsDatasetsFile)


def portals_sample():
    portals = [
        ["https://data.austintexas.gov", 'Austin', ' ', 'Socrata', '4419', '875463'],  # API ok
        ["https://data.cityofnewyork.us", 'New York', ' ', 'Socrata', '3259', '8272963'],  # API ok
        ["https://data.buffalony.gov", 'Buffalo', ' ', 'Socrata', '2365', '260041'],  # API ok
        ["https://data.cityofchicago.org", 'Chicago', ' ', 'Socrata', '1790', '2726772'],  # API ok
        ["https://data.lacity.org", 'Los Angeles', ' ', 'Socrata', '1703', '3883916'],  # API ok
        ["https://www.dallasopendata.com", 'Dallas', ' ', 'Socrata', '1173', '1259239'],  # API ok
        ['https://data.sfgov.org', 'San Francisco', ' ', 'Socrata', '1133', '839841'],  # API ok
        ["https://data.seattle.gov", 'Seattle', ' ', 'Socrata', '1094', '654224'],  # API ok
        ["https://data.honolulu.gov", 'Honolulu', ' ', 'Socrata', '373', '349275'],  # API ok
    ]
    return portals

if __name__ == '__main__':

    from comprehensive_set import compute_Comprehensive_Set
    from category_alignment import compute_Alignment
    from HVD_category import compute_HVD

    get=False
    usage=False
    CSC=False           # True to compute the Comprehensive_Set
    align=False         # True to compute the Alignment
    HVD=True            # True to compute HVD and print results into charts and tables

    portals=portals_sample()

    output_filename="AllPortalsDatasetsFile.json"

    ##  All datasets retrieve info. Ex:
    #
    # (id	"ni5x-u5hr"
    # city	"Austin"
    # name	"7916 Expense History Hid… Year 9 2022 2024 03 11"
    # uri	"https://data.austintexas.gov/dataset/ni5x-u5hr"
    # viewCount	3
    # downloadCount	3
    # category	"Unspecified")
    #
    ##  extracted from the portals

    ###  get usage data from portals
    portals_ETL(portals,output_filename,get,usage)  ###(A T T E N T I O N: rewriting 'output_filename')
    ###
    if CSC:
        compute_Comprehensive_Set()

    if align:
        compute_Alignment()

    if HVD:
        tablecatscities=False
        typeChart=False      #True to show HDVic in bar chart, False to show categories coverage in bar chart
        cats=False          #True to show aligned categories in Table, False to show 'o'
        compute_HVD(tablecatscities,typeChart,cats)    #Show charts, and write results in CSV