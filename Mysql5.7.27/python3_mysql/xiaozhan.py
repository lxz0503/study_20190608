import csv
with open('data.csv') as f:
    f_csv = csv.reader(f)
    for r in f_csv:
        print(r)   # each is a list
    # Row = namedtuple('Row', headings)  # this is a trick??? xiaozhan
    # for r in f_csv:
    #     yield Row(*r)