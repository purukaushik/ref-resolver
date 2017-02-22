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

    def __init__(self, id_):
        self.id = id_
        if id is not None:
            self.url_fragments = urlparse(id_)
        else:
            self.url_fragments = None

    def __str__(self):
        return repr(self.id + ", " + str(self.url_fragments))


def resolveInFile(jsonpath, fileObj):
    """
    Run through the `fileObj` json dict for the json path in `fragment` and return the object under the path.
    """
    path_expr = jsonpath_rw.parse("$" + ".".join(jsonpath.split("/")))
    matched_values = [match.value for match in path_expr.find(fileObj)]
    return matched_values[0] if len(matched_values) > 0 else None


def resolveRefFile(json_dump):
    """
    Resolves a ref schema file. If the file is in the cache, returns the contents from the cache.
    """
    if 'id' in json_dump:
        _id  = json_dump.get('id')
        if _id not in cache:
            cache[_id] = resolve(json_dump)
        return cache[_id]
    else:
        raise IdError("$ref-ed file has no `id`. Will not continue parsing anything. Go fix it!")

    
def parseAsFile(filename):
    """
    Opens and resolves a ref schema from file system.
    """
    json_dump = json.load(open(filename))
    return resolveRefFile(json_dump)


def parseAsHttp(url):
    """
    Use `requests` library to get json located at `url` and call `resolveRefFile` to resolve the $refs in the http-ed json further.
    """
    json_dump = None
    if callable(requests.Response.json):
        json_dump = requests.get(url).json()
    else:
        json_dump = requests.get(url).json
    return resolveRefFile(json_dump)


def parseRef(fragment, value):
    """
    Parse the $ref value and resolve using the scheme of resolution from `urlparse(value)`.
    """
    ref_frag = urlparse(value)
    ref_file = ref_frag.netloc + ref_frag.path
    # ref_frag ->ParseResult(scheme=u'http', netloc=u'localhost:3000', path=u'/ref_schema.json', params='', query='', fragment=u'/definitions/address')
    
    if ref_frag.scheme in ['http', 'https']:
        # http/https scheme retrieval of $refs
        _url = ref_frag.scheme + "://" + ref_file # -> http://localhost:3000/ref_schema.json
        http_file_json  = parseAsHttp(_url)
        return resolveInFile(ref_frag.fragment, http_file_json)
    elif ref_frag.scheme == 'file':
        # local file absolute and relative paths retrieval of $refs
        if isfile(ref_file):
            return resolveInFile(ref_frag.fragment,parseAsFile(ref_file))
        else:
            raise Exception("FileNotFoundException:: "+ ref_file)
    elif ref_frag.scheme == "":
    # same file internal $ref
        return resolveInFile(ref_frag.fragment, json.load(open(fragment.url_fragments.path)))
    else:
        raise Exception("Scheme of resolution: " + fragment.url_fragments.scheme + " is currently not supported")

    
def resolveInnerElement(fragment, elem):
    """
    Resolves inner elements of value attributes. Handles nesting gracefully with standard recursive procedures.
    """
    if isinstance(elem, dict):
        return parse(fragment, elem)
    elif isinstance(elem, list):
        return map(lambda x: resolveInnerElement(fragment, x), elem)
    else:
        return elem
    

def update(fragment, key, value):
    """
    Either resolves the value part if the key is `$ref` or just resolves the inner element in value recursively.
    """
    if "$ref" == key:
        parsedResult = parseRef(fragment, value)
        return parsedResult
    else:
        return {key: resolveInnerElement(fragment, value)}

    
def parse(fragment, json_dict):
    """
    Looks at every key-value pair in `json_dict`, resolves $refs and returns new dictionary
    containing resolutions.
    This method is not purely functional. It creates a mutable dictionary and puts things into it. Yuck!
    """
    mut_dict = {}
    for (key,value) in json_dict.iteritems():
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
        return parse(URLFragment(json_obj.get("id")), json_obj)


if __name__ == "__main__":
    self_ref_json = json.load(open('self_ref_test.schema.json'))
    #ejson = json.load(open('test_schema.json'))
    print resolve(self_ref_json)
