from jsonschema import RefResolver
import simplejson as json
from urlparse import urlparse

file = 'main.4.schema.json'
json_obj = json.load(open(file))

base_uri = ""
if "id" in json_obj:
    base_uri = json_obj["id"]

resolver = RefResolver(base_uri=base_uri, referrer=json_obj)

json = resolver.resolve_fragment(json_obj, "definitions/histogram")
print json
