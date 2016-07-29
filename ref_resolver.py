from urlparse import urlparse
import simplejson as json
from os.path import isfile
import jsonpath_rw

class RefResolver:

    def __init__(self):
        self.url_fragments = None

    def __init__(self, id):
        if id is not None:
            self.url_fragments = urlparse(id)
        else:
            self.url_fragments = None

    def resolve(self, json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == "$ref":
                    ref_frag = urlparse(value)
                    ref_file = ref_frag.netloc + ref_frag.path

                    if self.url_fragments.scheme in ['http', 'https']:
                        #todo: get file from http request
                        pass
                    elif self.url_fragments.scheme == 'file':

                        if isfile(ref_file):
                            # if the ref is another file -> go there and get it
                            json_dump = json.load(open(ref_file))
                            ref_id = None
                            if 'id' in json_dump:
                                ref_id = json_dump['id']

                            RefResolver(ref_id).resolve(json_dump)
                        else:
                            # if the ref is in the same file grab it from the same file
                            json_dump = json.load(open(self.url_fragments.netloc+self.url_fragments.path))
                        ref_path_expr = "$" + ".".join(ref_frag.fragment.split("/"))
                        path_expression = jsonpath_rw.parse(ref_path_expr)
                        list_of_values = [match.value for match in path_expression.find(json_dump)]

                        if len(list_of_values) > 0:
                            resolution = list_of_values[0]
                            return resolution

                resolved = self.resolve(value)
                if resolved is not None:
                    json_obj[key] = resolved
        elif isinstance(json_obj, list):
            for (key, value) in enumerate(json_obj):
                resolved = self.resolve(value)
                if resolved is not None:
                    json_obj[key] = resolved
        return None