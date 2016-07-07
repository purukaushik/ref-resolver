# ref-resolver
A python API to resolve `$ref` pointers in json-schemas and inline them. Supports relative file paths in $ref.

## Example code invocation

    import json
	from ref-resolver import resolve
	
	# grab python dict from json schema filea
	json-schema-file = json.loads('/path/to/your/example-schema.json')
	
	# call to API resolve method
	resolve(json-schema-file)
	
	# dict is now inlined with all $ref removed

## Example inlining

Example from the hubble telescope tutorial - https://spacetelescope.github.io/understanding-json-schema/structuring.html#structuring
   
   test_schema.json
   
    {
          "required": [
            "shipping_address"
          ],
          "properties": {
            "shipping_address": {
              "$ref": "ref_schema.json#\/definitions\/address"
            },
            "billing_address": {
              "$ref": "ref_schema.json#\/definitions\/address"
            }
          },
          "type": "object",
          "$schema": "http:\/\/json-schema.org\/draft-04\/schema#",
          "id": "test_schema.json"
     }
	 
 
