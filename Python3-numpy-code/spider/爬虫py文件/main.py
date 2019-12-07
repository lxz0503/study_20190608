from qunar import get_all_data
from qunar import dep_list
from multiprocessing import Pool

if __name__ == "__main__":
    pool=Pool()
    pool.map(get_all_data,dep_list.split())