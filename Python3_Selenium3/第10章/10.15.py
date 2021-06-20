import json
json_data1 = '{"j1": 1, "j2": 2, "j3": 3, "j4": 4}'
text_json = json.loads(json_data1)
print(text_json)
print(type(text_json))
