import xml.etree.ElementTree as ET
import pprint
import re



def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        atr = element.attrib
        if "uid" in atr:
            users.add(atr["uid"])
            
    return users
