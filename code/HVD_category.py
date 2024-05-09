import json
import portal
import report as rep
from portal import Portal


def merge_usage_match(portals_per_category_usage,portals_category_match):

    lstPortal = portal.read_portals_from_json_file(portals_per_category_usage)
    with open(portals_category_match, 'r') as json_file:
        allign = json.load(json_file)
        zipped=list(zip(allign,lstPortal))

    for portals_cats,portals_usage in zipped:
        dit = portals_usage.categories.items()
        dictdit = dict(dit)
        for k,v in iter(portals_cats[1].items()):
            dictdit[k].update({'map': v})

    return lstPortal

def datasets_per_portal(portal):
    count_portal_datasets=0
    for c in portal.categories.values():
        count_portal_datasets+=c['count']
    return count_portal_datasets

def datasets_in_portals_pool(portals):
    total_datasets=0
    for p in portals:
        total_datasets+=datasets_per_portal(p)
    return total_datasets


def HVD_for_category(portals_per_category_usage,portals_category_match):

    portals_categories_alligned = set()

    with open(portals_category_match, 'r') as json_file:
        data = json.load(json_file)
    for p in data:
        cats = p[1].values()
        portals_categories_alligned.update(cats)

    portals_categories_alligned = portals_categories_alligned - {""}      ### subset of CSC (computed on all US datasets),
                                                        ### and intersection with the alligned categories of portals sample pool

    total_datasets=datasets_in_portals_pool(portals_per_category_usage)

    cats_HVD=dict()

    for cat_in_CSC in portals_categories_alligned:
        cat_HVD = 0
        cat_count = 0
        cat_downl = 0
        cat_views = 0
        cat_portals=set()
        for p in portals_per_category_usage:
            for c in p.categories.values():
                if c['map']==cat_in_CSC:
                    total_portal_datasets=datasets_per_portal(p)
                    cat_HVD += c['HVDvalue']*(total_portal_datasets/total_datasets)
                    cat_count += c['count']
                    cat_downl += c['downl']
                    cat_views += c['views']
                    cat_portals.add(p.city)

        cat_dict=dict({'HVDvalue':cat_HVD,'count':cat_count,'downl':cat_downl,'views':cat_views,'portals':cat_portals,'num_portals':len(cat_portals)})
        cats_HVD.update({cat_in_CSC : cat_dict})

    print(cats_HVD)
    return cats_HVD



def compute_HVD(typeChart,cats):
#if __name__ == '__main__':

    output_dir = "output/"
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #    portalsFile = '../portals.json'
    portalsFile = output_dir+"portals_category_usage.json"

    categoryMatchFile = output_dir + 'portals_category_match_100_cities_all_synsets.json'

    table_categories_portals= 'table_categories_portals.csv'

    lstPortalUsageCatMerged=merge_usage_match(portalsFile, categoryMatchFile)

    HVD_4_cats=HVD_for_category(lstPortalUsageCatMerged, categoryMatchFile)

    if typeChart:
        rep.show_cats_HVD(HVD_4_cats)
    else:
        rep.show_cats_HVD(HVD_4_cats,'False')

    rep.table_cats_portals(HVD_4_cats, lstPortalUsageCatMerged,output_dir,table_categories_portals,cats)