from collections import defaultdict
import xml.etree.cElementTree as ET
import re
import codecs
import json
import map_info as MI
import map_wrangle as MW

#=======================
# Author: Jae Hee Lee
# 
# Wrangles Canberra's OpenStreetMap data
#
# 1. Portion of this code is referenced from the Udacity course quizzes that I completed.
# 
#=======================

# Constants
FILENAME = 'canberra_australia.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#Converts XML into JSON (Core Function)
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # Wrangle and transform created key (contains basic information about the tag)
        created = {}
        for attr_key in element.attrib.keys():
            if attr_key in CREATED:
                created[attr_key] = element.attrib[attr_key]
            elif  element.attrib[attr_key] == element.get('lat') or element.attrib[attr_key] == element.get('lon'):
                pos = []
                pos.append(float(element.get('lat')))
                pos.append(float(element.get('lon')))
                node['pos'] = pos
            else:
                node[attr_key] = element.get(attr_key)
                node['type'] = element.tag
        node['created'] = created
        
        # Wrangle and transform address and node_refs
        node_refs = []
        address = {}
        for sub_elem in element:
            #according to conditions outlined above (only tag and nd exists)
            if sub_elem.tag == 'tag':
                if re.search(r'\w+:\w+:\w+', sub_elem.get('k')):
                    pass
                elif re.search(problemchars, sub_elem.get('k')):
                    pass
                elif sub_elem.get('k').startswith('addr:'):
                    address[sub_elem.get('k')[5:]] = sub_elem.get('v')
                    node['address'] = address
                else:
                	# As there are many varities of keys other than some rather 'standardized' keys (such as uid), 
                	# these are not checked for validity.
                	node[sub_elem.get('k')] = sub_elem.get('v')
            elif sub_elem.tag == 'nd':
                node_refs.append(sub_elem.get('ref'))
                node['node_refs'] = node_refs
        
        #Auditing street name
        if(node.has_key("address") and node['address'].has_key("street")):
        	node['address']['street'] = MW.audit_street_name(node['address']['street'])
        
        #Auditing postcode name (As there are only two errors, it is okay to just fix those two errors.)
        if(node.has_key("address") and node['address'].has_key("postcode")):
        	if(node['address']['postcode'] == 'Yarralumla ACT 2600'):
        		node['address']['postcode'] = '2600'
        	if(node['address']['postcode'] == 'ACT 2604'):
        		node['address']['postcode'] = '2604'

        #Auditing city name (there are only few errors so it is okay to just fix it.)
        if(node.has_key("address") and node['address'].has_key("city")):
        	if(node['address']['city'] == 'CAMPBELL'):
        		node['address']['city'] = 'Campbell'
        	if(node['address']['city'] == 'Chisholm ACT'):
        		node['address']['city'] = 'Chisholm'
        	if(node['address']['city'] == 'Duntroon, ACT'):
        		node['address']['city'] = 'Duntroon'
        	if(node['address']['city'] == 'Canberra Airport'):
        		node['address']['city'] = 'Canberra'
        	if(node['address']['city'] == 'Canberra, Australia'):
        		node['address']['city'] = 'Canberra'

        #Auditing housenumber name (the only concern is unicode encoding error)
        if(node.has_key("address") and node['address'].has_key("housenumber")):
        	if(isinstance(node['address']['housenumber'], unicode)):
        		node['address']['housenumber'] = node['address']['housenumber'].encode('utf-8').replace('\xe2\x80\x93', '-')
        
        return node
    else:
        return None

# Writes JSON File
def convert_to_json(FILENAME, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(FILENAME)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(FILENAME):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent = 2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def run():
    #Map info related functions
    #tags = MI.count_tags(FILENAME)
    #keys = MI.process_map(FILENAME)
    #users = MI.get_unique_user(FILENAME)

    #Checking all unique values within addr:attribute
    #unique_streets = MW.get_unique_address_attribute_values(FILENAME, 'street')
    
    #Conversion
    #my_data = convert_to_json(FILENAME, True)
    #print my_data
    
if __name__ == "__main__":
    run()