import simplejson as json
from os.path import isfile
import jsonpath_rw
from jsonpath_rw import jsonpath
               

refList = list()

def parse(json_dict):
    #print "Looking at: " + str(json_dict)
    #print "Type is: " + str(type(json_dict))
    # must be one of -> string, dictionary, list
    if isinstance(json_dict,dict):
        # if it is a dictionary, iterate thru all key,value pairs and add them values whose keys are "$ref";
        # if key is not "$ref" leave it
        for key, value in json_dict.items():
            if key == "$ref":
                refList.append(value)
                file =  value.split("#")[0]
                refpath = value.split("#")[1]
                
                if isfile(file):
                    jsondump = json.load(open(file))
                    refpathexpr = "$" + ".".join(refpath.split("/"))
                    pathexpr = jsonpath_rw.parse(refpathexpr)
                    listofvalues = [match.value for match in pathexpr.find(jsondump)]

                    if len(listofvalues) > 0:
                        #print json_dict
                        #print listofvalues[0]
                        reparse = parse(listofvalues[0])
                        print reparse
                        print listofvalues[0]
                        return listofvalues[0]
            #print "~"
            #print str(key),str(value)            
            
            ret_val = parse(value)
            if ret_val is not None:
                #print key+ " : " + str(ret_val)
                json_dict[key] = ret_val
    elif isinstance(json_dict,list):
        for (key,value) in enumerate(json_dict):
            #print "#"
            ret_val = parse(value)
            if ret_val is not None:
                #print str(key) + ": " + str(ret_val)
                json_dict[key] = ret_val
    return None

#ydicT = json.load(open('main.4.schema.json'))
dicT = json.load(open('test_schema.json'))

parse(dicT)
new_file = open('test_schema_resolved.json', 'w')
#json.dump(dicT,new_file)

#import json, os
#from jsonschema import validate, ValidationError

#json1 = None
#with open('sample_v4_ping.json') as f1:
#with open('test_json.json') as f1:
#    json1 = json.load(f1)

#schemaJson = None
#with open('test_schema_resolved.json') as schema:
#    schemaJson = json.load(schema)

#from jsonschemaerror import check_json
#error = check_json(json1, dicT)

#print error

