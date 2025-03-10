# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 14:08:36 2019

@author: HG
"""

import json

class Portal:
    def __init__(self):
        self.city = ""
        self.url = ""
        self.coord = ""
        self.categorization = ""
        self.platform = ""
        self.categories = []




def read_portals_from_json_file(portals_file, platform=None):
    lst_portals = []
    with open(portals_file, 'r') as json_file:  
        data = json.load(json_file)
        for p in data:
            portal = Portal()
            portal.city = p.get("city")
            portal.url = p.get("url")
            portal.coord = p.get("coord")
            portal.categorization = p.get("categorization")
            portal.platform = p.get("platform")
            portal.categories = p.get('categories')
            lst_portals.append(portal)

    if platform:
        return [portal for portal in lst_portals if portal.platform == platform]
    else:
        return lst_portals

def all_categories(portals):
    categories = []
    [categories.extend(portal.categories) for portal in portals]
    return categories

def exclude_portals_without_category(portals):
    return [portal for portal in portals if len(portal.categories) > 0]