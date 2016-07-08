# ref-resolver
A python API to resolve `$ref` pointers in json-schemas and inline them. Supports relative file paths in $ref.

## Example code invocation

    import json
	from ref_resolver import resolve
	
	# grab python dict from json schema files
	json_schema_file = json.loads('/path/to/your/example-schema.json')
	
	# call to API resolve method
	resolve(json_schema_file)
	
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
              "$ref": "ref_schema.json#/definitions/address"
            },
            "billing_address": {
              "$ref": "ref_schema.json#/definitions/address"
            }
          },
          "type": "object",
          "$schema": "http://json-schema.org/draft-04/schema#",
          "id": "test_schema.json"
     }
	 
 ref_schema.json
 
    {
      "id" : "ref_schema.json",
      "$schema": "http://json-schema.org/draft-04/schema#",
    
      "definitions": {
        "address": {
          "type": "object",
          "properties": {
            "street_address": { "type": "string" },
            "city":           { "type": "string" },
            "state":          { "type": "string" },
			"code" : {"$ref": "#/definitions/code"}
          },
          "required": ["street_address", "city", "state"]
        },
          "code" : {
    	  "type" : "string"
          }
      },
    
      "type": "object",
      "properties" : {}
    
    }

Post-inlining:

test_schema.json

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "required": [
            "shipping_address"
        ],
        "type": "object",
        "properties": {
            "billing_address": {
                "required": [
                    "street_address",
                    "city",
                    "state"
                ],
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
                    },
                    "state": {
                        "type": "string"
                    },
                    "code": {
                        "type": "string"
                    },
                    "street_address": {
                        "type": "string"
                    }
                }
            },
            "shipping_address": {
                "required": [
                    "street_address",
                    "city",
                    "state"
                ],
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
                    },
                    "state": {
                        "type": "string"
                    },
                    "code": {
                        "type": "string"
                    },
                    "street_address": {
                        "type": "string"
                    }
                }
            }
        },
        "id": "test_schema.json"
    }
