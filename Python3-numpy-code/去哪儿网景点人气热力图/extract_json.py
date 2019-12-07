import pandas as pd
import json
df = pd.read_csv("D:/qunaer_sights.csv")
points = []
df = df[["经度","纬度","月销量"]]
for item in df.values:
    points.append({"lng":item[0],"lat":item[1],"count":item[2]})
str=json.dumps(points)
print(str)