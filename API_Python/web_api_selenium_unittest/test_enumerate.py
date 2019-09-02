
def test_enu(album):
    covert_list = enumerate(album, start=1)
    print(type(covert_list))
    for i in covert_list:
        print(type(i))
        print(i)


def test_zip(year, album):
    for year, album in zip(year, album):
        print('the result of zip is %s,%s' % (year, album))


if __name__ == '__main__':
    year = ['1976', '1234', '2356', '2018']
    album = ['aaa', 'bbb', 'ccc', 'ddd']
    test_enu(album)
    result_zip = test_zip(year, album)
    #print(result_zip)
