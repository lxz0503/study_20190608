# this is to read a large file with pandas

import pandas as pd


def pandas_read(filename, sep=',', size=5):
    reader = pd.read_csv(filename, sep, chunksize=size)
    while True:
        try:
            yield reader.get_chunk()
        except StopIteration:
            print('Done')
            break


if __name__ == '__main__':
    g = pandas_read('test_result.log', sep='\n')
    for c in g:
        print(c)