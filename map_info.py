import xml.etree.cElementTree as ET
import re

#=======================
# Author: Jae Hee Lee
# 
# Gets map information from Canberra's OpenStreetMap data
#
# 1. Portion of this code is referenced from the Udacity course quizzes that I completed.
# 
#=======================

# RegExs
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Counting all the tags and sort them out based on their key
def count_tags(filename):
	d = dict()
	for event, elem in ET.iterparse(filename):
		if(elem.tag not in d):
			d[elem.tag] = 1
		elif(elem.tag in d):
			d[elem.tag] += 1
	return d

# Sorting out
def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        for tag in element.iter("tag"):
            if(re.match(lower,tag.attrib['k']) != None):
                keys['lower'] += 1
            elif(re.match(lower_colon,tag.attrib['k']) != None):
                keys['lower_colon'] += 1
            elif(re.match(problemchars,tag.attrib['k']) != None):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

# Get User Info
def get_user(element):
    return element.attrib['user']

# Get All Users (No Duplicates)
def get_unique_user(filename):
	users = set()
	for _, element in ET.iterparse(filename):
		if( 'user' in element.attrib):
			users.add(get_user(element))
	return users