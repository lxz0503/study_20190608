import yaml
#以下为将yaml格式数据转化为Python list 数据类型的数据。
file_2 = open('config6.yml')
yml = yaml.load(file_2,Loader=yaml.FullLoader)
print(yml)
print(type(yml))
#以下为将yaml格式的数据转化为复合类型的数据，其中包含list和字典数据类型。
file_3 = open('config6.yml')
yml_3 = yaml.load(file_3,Loader=yaml.FullLoader)
print(yml_3)
print(type(yml_3))	
