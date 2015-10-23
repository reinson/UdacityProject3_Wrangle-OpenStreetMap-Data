import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
             
        node["pos"] = ["NA","NA"]
        node["created"] = {}
        node["type"] = element.tag
              
        for attribute in element.attrib:            
            value = element.attrib[attribute]

            if attribute in CREATED:
                node["created"][attribute] = value
            elif attribute == "lon": 
                node["pos"][1] = float(value)
            elif attribute == "lat":
                node["pos"][0] = float(value)
            else:
                node[attribute] = value
                      
            for tag in element.iter("tag"):                                
                k = tag.attrib["k"]
                v = tag.attrib["v"]
                
                if not re.search(problemchars,k) and k.count(":") < 2:
                    if k[0:5] == "addr:":
                        k = k[5:]                     
                        
                        if "address" not in node:
                            node["address"] = {}                            
                        node["address"][k] = v
                        
                    else:
                        node[k] = v

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
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
