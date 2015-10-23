import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    result = {}
    gen = ET.iterparse(filename)
    for event, elem in gen:
        tag = elem.tag
        if tag in result:
            result[tag] += 1
        else:
            result[tag] = 1
    return result
