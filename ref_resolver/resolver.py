from urlparse import urlparse, urljoin
import simplejson as json
from os.path import isfile
import jsonpath_rw
import requests
import logging


logging.basicConfig(level=logging.DEBUG)


def debug(message):
    logging.debug(message)
    
def info(message):
    logging.info(message)
    
cache = {}

class IdError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class URLFragment(object):

    def __init__(self):
        self.url_fragments = None

    def __init__(self, id_):
        self.id = id_
        if id is not None:
            self.url_fragments = urlparse(id_)
        else:
            self.url_fragments = None


def resolveInFile(fragment, fileObj):
    path_expr = jsonpath_rw.parse("$" + ".".join(fragment.fragment.split("/")))
    matched_values = [match.value for match in path_expr.find(fileObj)]
    return matched_values[0] if len(matched_values) > 0 else None
    
#def parseAsFile(filename):

    
def parseAsHttp(url, ref_file):
    debug("parseAsHttp:: " + url + ", "+ ref_file)
    json_dump = None
    if callable(requests.Response.json):
        json_dump = requests.get(url).json()
    else:
        json_dump = requests.get(url).json
    if 'id' in json_dump:
        cache[ref_file] = resolve(json_dump)
        return cache[ref_file]
    else:
        raise IdError("$ref-ed file has no `id`. Will not continue parsing anything. Go fix it!")
        

def parseRef(fragment, value):
    ref_frag = urlparse(value)
    ref_file = ref_frag.netloc + ref_frag.path
    if ref_file in cache:
        return cache[ref_file]
    else:
        if fragment.url_fragments.scheme in ['http', 'https']:
            # http/https scheme retrieval of $refs
            return parseAsHttp(urljoin(fragment.url_fragments.scheme, fragment.id, ref_file), ref_file)
        #elif fragment.url_fragments.scheme == 'file' and isfile(ref_file):
            # local file absolute and relative paths retrieval of $refs
        #    return parseAsFile(ref_file)
        #elif fragment.url_fragments.scheme == "":
            # same file internal $ref
        #    return parseAsFile(fragment.url_fragments.netloc + fragment.url_fragments.path)
        else:
            raise Exception("Scheme of resolution: " + fragment.url_fragments.scheme + " is currently not supported")
        

def update(fragment, key, value):
    if "$ref" == key:
        debug("update$ref:: " + key)
        return parseRef(fragment, value)
    else:
        return {key: apropose(fragment, value)}

def apropose(fragment, elem):
    debug("apropose:: ")
    if isinstance(elem, dict):
        return parse(fragment, elem)
    elif isinstance(elem, list):
        return map(lambda x: apropose(fragment, x), elem)
    else:
        return elem
        
def parse(fragment, json_dict):
    mut_dict = {}
    for (key,value) in json_dict.iteritems():
        debug("parse:: " + key)
        mut_dict.update(update(fragment, key, value))
    return mut_dict


def resolve(json_obj):
    """
    Resolves $ref in the `json_obj` and returns a `dict` that has inlined $ref elements.
    Raises an `IdError` if the `id` key is not present in the `json_obj`.
    """
    if 'id' not in json_obj:
        raise IdError("No `id` field in passed parameter")
    else:
        debug("resolve::" + json_obj.get('id'))
        return parse(URLFragment(json_obj.get("id")), json_obj)


if __name__ == "__main__":
    ejson = json.load(open('test_schema.json'))
    print resolve(ejson)
