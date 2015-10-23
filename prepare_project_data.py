#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
street_name_map = {"MNT":"mnt","maantee":"mnt","puiestee":"pst","MNT.":"mnt"}


def add_to_list(given_list,element):
    #Gets called for house number grouping
    #Adds a house number into the list, if it is not already there 
    if type(given_list) == type("str"):
        given_list = [given_list]
    if element not in given_list:
        given_list = given_list + [element]
    return given_list

def shape_element(element):
    #Shapes a XML element into a python dictionary that will be turned into a json object
    node = {} 

    if element.tag == "node" or element.tag == "way" : #only elements of type node and way will be included
       
        node["pos"] = ["NA","NA"]
        node["created"] = {}
        node["type"] = element.tag
       
        for attribute in element.attrib:

            if attribute in CREATED:
                node["created"][attribute] = element.attrib[attribute]
            elif attribute == "lon": 
                node["pos"][1] = element.attrib[attribute]
            elif attribute == "lat":
                node["pos"][0] = element.attrib[attribute]
            else:
                node[attribute] = element.attrib[attribute]
            
            
            for tag in element.iter("tag"): 
                #iterate over all the element's tags
                k = tag.attrib["k"] #key
                v = tag.attrib["v"] #value

                if not re.search(problemchars,k) and k.count(":") < 2:
                    #only process tags that do not contain incompatible characters or not more than 1 colon 
                    if k == "address": 
                        #special treatment for the tag name that is incompatible  with predefined data model
                        if "address" not in node:
                            node["address"] = {}
                        node["address"]["postal address"] = v                        
                        
                    elif k[0:5] == "addr:":
                        k = k[5:] #update key value, get rid of "addr:" beginning
                        if "address" not in node:
                            node["address"] = {}
                       
                        if k[:11] == "housenumber": 
                           #adds different house numbers (housenumber, housenumber2, etc) into one list
                            if "housenumber" not in node["address"]:
                                node["address"]["housenumber"] = []
                            node["address"]["housenumber"] = add_to_list(node["address"]["housenumber"],v.lower())
                        else:
                            if k == "street":
                                #Unifies different abbrevations of street name endings
                                v_ending = v.split(" ")[-1]
                                if v_ending in street_name_map:
                                    v_new_end = street_name_map[v_ending]
                                    v = v.replace(v_ending,v_new_end)
                            node["address"][k] = v 
                        
                    else:
                        node[k] = v

        if "address" in node:
            #some house numbers contain an apartment number (as 12/7, house/apartment)
            #this block removes the apartment numbers from house number fields and collects them into separate apartments field
            if "housenumber" in node["address"]:                               
                housenumbers = node["address"]["housenumber"]
                new_nrs = []
                apartments = {}
                for nr in housenumbers: 
                    if nr.count("/") == 1: 
                        new_nr, apartment = nr.split("/")
                        if new_nr not in apartments:
                            apartments[new_nr] = []
                        apartments[new_nr] = apartments[new_nr] + [apartment]
                        if new_nr not in new_nrs:
                            new_nrs += [new_nr]                        
                    else:
                        new_nrs += [nr]

                node["address"]["housenumber"] = new_nrs
                
                if apartments != {}:
                    node["address"]["apartments"] = apartments
    
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    count = 0
    with codecs.open(file_out, "w") as fo:
        
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
                       
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('sample', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    pprint.pprint(data[0])
    pprint.pprint(correct_first_elem)
    
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()
    
