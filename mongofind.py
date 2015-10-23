
#This file contains some code for creating mongoDB queries and aggregation pipelines.


from pymongo import MongoClient
import pprint
import re

client = MongoClient("mongodb://localhost:27017")
db = client.db.tartumaa
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

def find(): #contains some example queries used for cleaning the data
    #query = {"address.apartments":"{'1':['8']}","address.housenumber":["1"]}
    #query = {"address.street": "Tammeoksa","address.housenumber":["1"]}
    #query = {"created.user":"jaakl"}
    query = {"address.housenumber":{"$exists":1}}
   #query = {"address.street":"Selleri"}
    #query = {"address.housenumber":{"$regex":"[1-9]+\/[1-9]+"}}
    #query = {"id": '212397628'}
    result = db.find(query)

    #result = db.find_one()
    #print result
    count = 0
    for i in result:
        a = i["address"]["housenumber"]
        for u in a:
            if "/" in u:
                print i
#        pprint.pprint(i)
        count += 1
    print  count



def make_pipeline():
   
    #What user has created the most housenumber2 tags
    pipeline = [
        {"$match":{"address.housenumber2":{"$regex":"[1-9]+"}}},
        {"$group" : {"_id" : "$created.user",
                     "count" : {"$sum":1}}},
        {"$sort": {"count":-1}}
    ]

    pipeline2 = [
        {"$group" : {"_id" : "$address.street",
                 "count": {"$sum":1}}},
        {"$sort" : {"count":1}}

    ]
    
    #what street has the most buildings:
    pipeline3 = [{"$match":{"address.street":{"$exists":1}}},
                {"$unwind" : "$address.housenumber"},
                {"$group" : {"_id" : {"city": "$address.city",
                                      "street": "$address.street"},
                             "count" : {"$sum" : 1},
                             "buildings" : {"$addToSet" : "$address.housenumber"}}},
    
                 {"$unwind":"$buildings"},
                 {"$group":{"_id":{"city":"$_id.city",
                                   "street":"$_id.street"},
                            "nr_of_buildings":{"$sum":1}}},
                 {"$sort":{"nr_of_buildings":-1}},
                 {"$limit":10}
    ]

    #how many buildings on a street on average
    pipeline5 = [{"$match":{"address.street":{"$exists":1}}},
                {"$unwind" : "$address.housenumber"},
                {"$group" : {"_id" : {"city": "$address.city",
                                      "street": "$address.street"},
                             "count" : {"$sum" : 1},
                             "buildings" : {"$addToSet" : "$address.housenumber"}
                         }},
    
                 {"$unwind":"$buildings"},
                 {"$group":{"_id":{"city":"$_id.city",
                                   "street":"$_id.street"},
                            "nr_of_buildings":{"$sum":1}}},
                 {"$group":{"_id":"$_id.city",
                        "buildings_on_street":{"$avg":"$nr_of_buildings"}}},
                 {"$sort":{"buildings_on_street":-1}},
                 {"$limit":10}
    ]
    
    pipeline4 = [
        {"$match":{"address.housenumber":{"$exists":1},
               "address.street":{"$exists":False}}},
        #{"$group" : {"_id" : "$created.user",
        #             "count" : {"$sum":1}}},
        #{"$sort": {"count":-1}}
    ]


    return pipeline5

def aggregate():
    pipeline = make_pipeline()
    result = db.aggregate(pipeline)
    pprint.pprint(result["result"])
    #return result

aggregate()    

#find()
