from collections import defaultdict
import xml.etree.cElementTree as ET
import re
import codecs

#=======================
# Author: Jae Hee Lee
# 
# Wrangles Canberra's OpenStreetMap data
#
# 1. Main.py uses functions in this code.
# 2. Portion of this code is referenced from the Udacity course quizzes that I completed.
# 
#=======================

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected_street_types = ["Antill", "Avenue", 
                        "Bank", "Boulevard", 
                        "Circle", "Circuit", "Close", "Court", "Commons", "Crescent", 
                        "Drive", 
                        "Highway", 
                        "Lane",
                        "Parkway", "Place", 
                        "Road",
                        "Street", "Square", 
                        "Trail", "Terrace", 
                        "Walk", "Way", 
                        "Quay",
                        "View"]

mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd." : "Road",
            "Cct" : "Circuit"}

# Determines whether current attribute key is "addr:attribute_name"
def is_attribute_name(elem, attribute_name):
    return (elem.attrib['k'] == "addr:" + attribute_name)

# Returns all unique values that has a key of "attr:attribute_name"
def get_unique_address_attribute_values(filename, attribute_name):
    filename = open(filename, "r")
    unique_attribute_values = set()
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_attribute_name(tag, attribute_name):
                    unique_attribute_values.add(tag.attrib['v'])
    return unique_attribute_values

# Used to parse irregular street names
def parse_street_name(street_name):
    if(',' in street_name):
        street_name_candidates = street_name.split(',')
        #Between two candidates, selects one that contains the expected street type
        for street_name in street_name_candidates:
            if(any(str_type in street_name for str_type in expected_street_types)):
                return street_name
    elif('&' in street_name):
        #These types of streets usually are intersecting to each other. Chose the main road (the later one).
        return street_name.split('&')[1]

    return street_name

# Used to audit street name
def audit_street_name(street_name):
    street_name = parse_street_name(street_name)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_type = update_name(street_type, mapping)
        if street_type in expected_street_types:
            return street_name
        elif street_type not in expected_street_types:
            for str_type in expected_street_types:
                if str_type in street_name:
                    str_index = street_name.find(str_type)
                    return street_name[:str_index + len(str_type)]

# Used to update abbreviation to its full name
def update_name(name, mapping):
    m = street_type_re.search(name)
    if(m.group(0) in mapping):
    	name = re.sub(street_type_re, mapping[m.group(0)], name)
    return name