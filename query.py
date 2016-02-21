#=======================
# Author: Jae Hee Lee
# 
# Explores Canberra's OpenStreetMap data (which is already wrangled)
#
# 1. To run this code, one must import 'canberra_austraila.osm.json' in canberra collection in openstreet database.
# 2. Portion of this code is referenced from the Udacity course quizzes that I completed.
# 
#=======================

from pymongo import MongoClient

#returns db object
def get_db(db_name):
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

#returns more legible list
def prettify_list(given_list):
	counter = 1
	print "==============================================="
	for elem in given_list:
		print "( count : " + str(elem['count']) + ") " + elem['_id'] + " is ranked " + str(counter)
		counter += 1
	print "==============================================="

#returns basic statistics about the given and total amounts
def prettify_basic_statistics(given_amount, total_amount, round_off = 2):
	return str(given_amount) + " / " + str(total_amount) + " (" + str(round(float(given_amount) / float(total_amount) * 100, round_off)) + "%)"

if __name__ == "__main__":
    db = get_db('openstreet_fake')

    #================================
    #	Basic Properties
    #================================

    #How many documents in the canberra collection
    total_documents = db.canberra.find().count()
    print "# of documents: " + str(total_documents)

    #How many nodes in this collection
    total_nodes = db.canberra.find({"type":"node"}).count()
    print "# of nodes: " + prettify_basic_statistics(total_nodes, total_documents)

    #How many nodes in this collection
    total_ways = db.canberra.find({"type":"way"}).count()
    print "# of ways: " + prettify_basic_statistics(total_ways, total_documents)

    #Number of unique users
    total_users = len(db.canberra.distinct("created.user"))
    print "# of unique users: " + str(total_users)

    #Unique Streets
    print "# of unique streets: " + str(len(db.canberra.distinct("address.street")))

    #Unique Postcode
    print "# of unique postcode: " + str(len(db.canberra.distinct("address.postcode")))

    #================================
    # Relatively Complex Queries
    #================================

    # Get the top-most contributed user
    top_user =  list(db.canberra.aggregate([{"$group" : {"_id" : "$created.user", "count" : {"$sum" : 1}}}, {"$sort" : {"count" : -1}}, {"$limit" : 1}]))
    prettify_list(top_user)
    
    # Get the specific part of the map via using the pos (find the nodes within the given area)
    map_query = { "pos.0" : {"$gte": -35.2875, "$lte":-35.2724}, "pos.1" : {"$gte": 149.1096, "$lte": 149.1304} }
    map_projection = {"_id" : 0, "created.uid" : 1}

    # # of users contributed in specified area
    map_contributed_users = db.canberra.find(map_query, map_projection)
    unique_users = set()
    for user in map_contributed_users:
    	unique_users.add(user['created']['uid'])
    
    # # of nodes and ways in specified area
    count_specific_area_nodes = map_contributed_users.count()
    print "# of users contributed in specified area: " + prettify_basic_statistics(len(unique_users), total_users)
    print "# of nodes and ways in specified area: " + prettify_basic_statistics(count_specific_area_nodes, total_documents)

    # Information about Yarralumla (2600) and Braddon (2612)
    postcode_query = {"type" : "node", "address.postcode" : {"$in" : ['2600', '2612']}}
    postcode_projection = {"_id" : 0, "created.uid" : 1}
    specific_area_nodes = db.canberra.find(postcode_query, postcode_projection)    
    
    unique_users = set()
    for user in specific_area_nodes:
    	unique_users.add(user['created']['uid'])
    print "# of users contributed to 2600 and 2612: " + prettify_basic_statistics(len(unique_users), total_users)

    count_specific_area_nodes = specific_area_nodes.count()
    print "# of nodes and ways in 2600 and 2612: " + prettify_basic_statistics(count_specific_area_nodes, total_documents, 5)

    #Top 3 biggest religion in Canberra
    biggest_religion = list(db.canberra.aggregate([{"$match" : {"amenity" : {"$exists": 1} , "amenity" : "place_of_worship"}}, 
    								  {"$group" : {"_id" : "$religion", "count": {"$sum" : 1}}}, 
    								  {"$sort" : {"count" : -1}}, 
    								  {"$limit" : 3}]))
    prettify_list(biggest_religion)

    #Top 10 amenities in Canberra region
    biggest_amenities = list(db.canberra.aggregate([{"$match" : {"amenity" : {"$exists" : 1}}}, 
    								  {"$group" : {"_id" : "$amenity", "count" : {"$sum" : 1}}}, 
    								  {"$sort" : {"count" : -1}}, 
    								  {"$limit" : 10}]))
    prettify_list(biggest_amenities)

    #The top 5 common streets in Canberra region 
    common_streets = list(db.canberra.aggregate([{"$match" : {"address.street" : {"$exists" : 1}}}, 
    								  {"$group" : {"_id" : "$address.street", "count" : {"$sum" : 1}}}, 
    								  {"$sort" : {"count" : -1}}, 
    								  {"$limit" : 5}]))
    prettify_list(common_streets)

    # The most-30-frequent period in which these nodes were created (is it outdated data?)
    common_time = list(db.canberra.aggregate([{"$group" : {"_id" : "$created.timestamp", "count" : {"$sum" : 1}}}, 
    								  {"$sort" : {"count" : -1}}, 
    								  {"$limit" : 30}]))
    prettify_list(common_time)

    time_query = { "created.timestamp" : {"$gte": '2014-01-01T00:00:00Z', "$lte": '2016-02-20T00:00:00Z'}}
    time_projection = {"_id" : 0, "created.uid" : 1}
    specific_time_nodes = db.canberra.find(time_query, time_projection).count()
    print "# of up-to-date documents: " + prettify_basic_statistics(specific_time_nodes, total_documents)

    time_query = { "created.timestamp" : {"$lt": '2014-01-01T00:00:00Z'}}
    specific_time_nodes = db.canberra.find(time_query, time_projection).count()
    print "# of outdated documents: " + prettify_basic_statistics(specific_time_nodes, total_documents)