import requests
import urllib.request
import pymongo
import time

client = pymongo.MongoClient('localhost', 27017)
book_qunar = client['qunar']
sheet_qunar_zyx = book_qunar['qunar_zyx']

def get_list(dep,item):
    url = 'https://touch.dujia.qunar.com/list?modules=list,bookingInfo&dep={}&query={}&mtype=all&ddt=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&et=FreetripTouch&date=&configDepNew=&needNoResult=true&originalquery={}&limit=0,20&includeAD=true&qsact=search'.format(
        urllib.request.quote(dep), urllib.request.quote(item), urllib.request.quote(item))
    strhtml = get_json(url)
    routeCount = int(strhtml['data']['limit']['routeCount'])
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

def get_all_data(dep):
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

dep_list = '''
    马鞍山
    茂名
    眉山
    梅州
    绵阳
    牡丹江
    武汉
    乌鲁木齐
    万宁
    潍坊
    威海
    渭南
    文昌
    文山
    温州
    乌海
    芜湖
    五家渠市
    乌兰察布
    武威
    无锡
    武夷山市
    五指山
    吴忠
    梧州
    郑州
    枣庄
    彰化
    张家界
    张家口
    张掖
    漳州
    湛江
    肇庆
    昭通
    镇江
    中山
    中卫
    周口
    舟山
    珠海
    驻马店
    株洲
    淄博
    自贡
    资阳
    遵义
    日喀则
    日照
    瑞金市
    北京
    白城
    百色
    白沙
    白山
    白银
    保定
    宝鸡
    保山
    保亭
    包头
    巴彦淖尔
    巴音郭楞
    巴中
    北海
    蚌埠
    本溪
    毕节
    滨州
    博尔塔拉
    亳州
    上海
    沈阳
    石家庄
    三门峡
    三明
    三沙
    三亚
    商洛
    商丘
    上饶
    山南
    汕头
    汕尾
    韶关
    绍兴
    邵阳
    神农架
    深圳
    石河子
    十堰
    石嘴山
    双鸭山
    朔州
    四平
    松原
    绥化
    遂宁
    随州
    宿迁
    宿州
    苏州
    济南
    佳木斯
    吉安
    江门
    焦作
    嘉兴
    嘉峪关
    揭阳
    吉林市
    金昌
    晋城
    景德镇
    荆门
    荆州
    金华
    济宁
    晋中
    锦州
    九江
    酒泉
    鸡西
    济源
    长春
    长沙
    成都
    重庆
    沧州
    常德
    昌都
    长葛市
    昌吉
    长治
    常州
    巢湖
    朝阳市
    潮州
    承德
    澄迈
    郴州
    赤峰
    池州
    崇左
    楚雄
    滁州
    西安
    香港
    西宁
    厦门
    湘潭
    湘西
    襄阳
    咸宁
    仙桃
    咸阳
    孝感
    西昌市
    锡林郭勒盟
    西南中沙群岛办事处
    兴安盟
    邢台
    新乡
    信阳
    新余
    忻州
    西双版纳
    宣城
    许昌
    徐州
    黔东南
    潜江
    黔南
    黔西南
    青岛
    庆阳
    清远
    秦皇岛
    钦州
    琼海
    琼中
    齐齐哈尔
    七台河
    泉州
    曲靖
    衢州
    南昌
    南京
    南宁
    南充
    南平
    南通
    南投
    南阳
    那曲
    内江
    宁波
    宁德
    怒江
    台北
    太原
    天津
    塔城地区
    泰安
    台中
    台州
    泰州
    唐山
    天水
    铁岭
    铜川
    通化
    通辽
    铜陵
    铜仁
    吐鲁番
    图木舒克
    屯昌
    鄂尔多斯
    恩施
    鄂州
    大理
    大连
    丹东
    淡水
    儋州
    大庆
    大同
    大兴安岭
    达州
    德宏
    德阳
    德州市
    定安
    定西
    迪庆
    东方
    东莞
    东营
    敦煌市
    兰州
    拉萨
    来宾
    莱芜
    廊坊
    乐东
    乐山
    凉山州
    连云港
    聊城
    辽阳
    辽源
    丽江
    临沧
    临汾
    临高
    陵水
    临夏
    临沂
    林芝
    丽水
    六安
    六盘水
    柳州
    陇南
    龙岩
    娄底
    漯河
    洛阳
    泸州
    吕梁
    澳门
    阿坝州
    阿克苏地区
    阿拉尔
    阿拉善盟
    阿勒泰
    阿里
    安康
    安庆
    鞍山
    安顺
    安阳
    广州
    贵阳
    甘南
    赣州
    甘孜州
    高雄
    广安
    广元
    贵港
    桂林
    果洛藏族自治州
    固原
    昆明
    开封
    喀什
    克拉玛依
    克孜勒苏柯尔克孜
    克孜勒苏
    盘锦
    攀枝花
    平顶山市
    平凉
    萍乡
    普洱
    普宁
    莆田
    濮阳
    福州
    防城港
    佛山
    抚顺
    阜新
    阜阳
    抚州
    银川
    雅安
    延安
    延边
    盐城
    阳江
    阳泉
    扬州
    延吉市
    烟台
    宜宾
    宜昌
    伊春
    宜春
    伊犁
    伊犁哈萨克自治州
    营口
    鹰潭
    义乌市
    益阳
    永州
    岳阳
    玉林
    榆林
    运城
    云浮
    玉树藏族自治州
    玉溪
    哈尔滨
    海口
    杭州
    合肥
    呼和浩特
    海北藏族自治州
    海东地区
    海南藏族自治州
    海西蒙古族藏族自治州
    哈密
    邯郸
    汉中
    鹤壁
    河池
    鹤岗
    黑河
    衡水
    衡阳
    和田
    河源
    菏泽
    贺州
    红河
    淮安
    淮北
    怀化
    淮南
    黄冈
    黄南藏族自治州
    黄山
    黄石
    惠州
    葫芦岛
    呼伦贝尔
    湖州
'''