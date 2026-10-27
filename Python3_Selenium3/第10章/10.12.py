import csv
csvfile = "test.csv"
c = csv.reader(open(csvfile,"r"))

#获取 c对象的类型
print(type(c))

for cs in c:
    for i in range(len(cs)):
        #print(type(cs[i]))
        print(cs[i])
