import csv
csvfile = "test.csv"
c = csv.reader(open(csvfile,'r'))
for cs in c:
    print(cs[0])
