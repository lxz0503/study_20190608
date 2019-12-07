import requests
import urllib
import time
import pymongo

client=pymongo.MongoClient('localhost',27017)
book_qunar=client['qunar']
sheet_qunar_zyx=book_qunar['qunar_zyx']
#
#
# url='https://touch.dujia.qunar.com/depCities.qunar'
# strhtml=requests.get(url)
# dep_dict=strhtml.json()
# for dep_item in dep_dict['data']:
#     for dep in dep_dict['data'][dep_item]:
#         a = []
#         print(dep)
#         url = 'https://m.dujia.qunar.com/golfz/sight/arriveRecommend?dep={}&exclude=&extensionImg=255,175'.format(urllib.request.quote(dep))
#         time.sleep(1)
#         strhtml = requests.get(url)
#         arrive_dict = strhtml.json()
#         for arr_item in arrive_dict['data']:
#             for arr_item_1 in arr_item['subModules']:
#                 for query in arr_item_1['items']:
#                     if query['query']  not in a:
#                         a.append(query['query'])
#         for item in a:
#             url = 'https://touch.dujia.qunar.com/list?modules=list,bookingInfo&dep={}&query={}&mtype=all&ddt=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&et=FreetripTouch&date=&configDepNew=&needNoResult=true&originalquery={}&limit=0,20&includeAD=true&qsact=search'.format(urllib.request.quote(dep),urllib.request.quote(item),urllib.request.quote(item))
#             time.sleep(1)
#             strhtml = requests.get(url)
#             routeCount=int(strhtml.json()['data']['limit']['routeCount'])
#             for limit in range(0, routeCount, 20):
#                 url = 'https://touch.dujia.qunar.com/list?modules=list,bookingInfo&dep={}&query={}&mtype=all&ddt=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&et=FreetripTouch&date=&configDepNew=&needNoResult=true&originalquery={}&limit={},20&includeAD=true&qsact=search'.format(
#                     urllib.request.quote(dep), urllib.request.quote(item),
#                     urllib.request.quote(item),limit)
#                 time.sleep(1)
#                 strhtml = requests.get(url)
#                 result = {
#                     'date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
#                     'dep': dep,
#                     'arrive': item,
#                     'limit': limit,
#                     'result': strhtml.json()
#                 }
#                 print(strhtml.text)
#                 sheet_qunar_zyx.insert_one(result)

def get_list(dep,item):
    url = 'https://touch.dujia.qunar.com/list?modules=list,bookingInfo&dep={}&query={}&mtype=all&ddt=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&et=FreetripTouch&date=&configDepNew=&needNoResult=true&originalquery={}&limit=0,20&includeAD=true&qsact=search'.format(
        urllib.request.quote(dep), urllib.request.quote(item), urllib.request.quote(item))
    strhtml = get_json(url)
    try:
        routeCount = int(strhtml['data']['limit']['routeCount'])
    except:
        return
    for limit in range(0, routeCount, 20):
        url = 'https://touch.dujia.qunar.com/list?modules=list,bookingInfo&dep={}&query={}&mtype=all&ddt=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&et=FreetripTouch&date=&configDepNew=&needNoResult=true&originalquery={}&limit={},20&includeAD=true&qsact=search'.format(
            urllib.request.quote(dep), urllib.request.quote(item),
            urllib.request.quote(item), limit)
        strhtml = get_json(url)
        result = {
            'date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
            'dep': dep,
            'arrive': item,
            'limit': limit,
            'result': strhtml
        }
        sheet_qunar_zyx.insert_one(result)

def connect_mongo():
    client=pymongo.MongoClient('localhost',27017)
    book_qunar=client['qunar']
    return book_qunar['qunar_zyx']


def get_json(url):
    strhtml=requests.get(url)
    time.sleep(1)
    return strhtml.json()

if __name__ == "__main__":

    url='https://touch.dujia.qunar.com/depCities.qunar'
    dep_dict=get_json(url)
    for dep_item in dep_dict['data']:
        for dep in dep_dict['data'][dep_item]:
            a = []
            url = 'https://m.dujia.qunar.com/golfz/sight/arriveRecommend?dep={}&exclude=&extensionImg=255,175'.format(urllib.request.quote(dep))
            arrive_dict = get_json(url)
            for arr_item in arrive_dict['data']:
                for arr_item_1 in arr_item['subModules']:
                    for query in arr_item_1['items']:
                        if query['query'] not in a:
                            a.append(query['query'])
            for item in a:
                get_list(dep,item)