import simplejson as json
from os.path import isfile
import jsonpath_rw

def parse(json_dict, filename):
    # must be one of -> string, dictionary, list
    if isinstance(json_dict, dict):
        # if it is a dictionary, iterate thru all key,value pairs
        for key, value in json_dict.items():
            # if you see a $ref - get the corresponding content from the ref place and return it
            if key == "$ref":
                uri_fragments = value.split("#")
                ref_uri_filename = uri_fragments[0]
                refpath = uri_fragments[1]

                if not ref_uri_filename.strip():
                    ref_uri_filename = filename
                if isfile(ref_uri_filename):
                    jsondump = json.load(open(ref_uri_filename))
                    refpathexpr = "$" + ".".join(refpath.split("/"))
                    pathexpr = jsonpath_rw.parse(refpathexpr)
                    listofvalues = [match.value for match in pathexpr.find(jsondump)]

                    if len(listofvalues) > 0:
                        resolution = listofvalues[0]
                        recursive_parse = parse(resolution, ref_uri_filename)
                        return resolution
            # just parse the value
            # and if the return is not None -> replace object. that's a $ref being replaced.
            resolved = parse(value, filename)
            if resolved is not None:
                json_dict[key] = resolved
    elif isinstance(json_dict, list):
        for (key, value) in enumerate(json_dict):

            resolved = parse(value, filename)
            if resolved is not None:
                json_dict[key] = resolved
    return None