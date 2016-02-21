import filecmp

#=======================
# Author: Jae Hee Lee
# 
# Compares file
#
# Every time I generate JSON file I compare with the previously generated file to examine whether there were any changes with the file. 
# 
#=======================

print filecmp.cmp('prev_canberra_australia.osm.json', 'canberra_australia.osm.json')