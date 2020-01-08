# *_* coding : UTF-8 *_*
# 开发团队   ：明日科技
# 开发人员   ：Administrator
# 开发时间   ：2019/7/2  16:43
# 文件名称   ：demo.py
# 开发工具   ：PyCharm
listcar = [[837624,"RAV4"],[791275,"途观"],[651090,"索罗德"],[1080757,"福特F系"],[789519,"高尔夫"],[747646,"CR-V"],[1181445,"卡罗拉"]]
listcha2=['莱科宁 236','汉密尔顿 158','维泰尔 214','维斯塔潘 216','博塔斯 227']
listcha3=['236 莱科宁','358 汉密尔顿','294 维泰尔','216 维斯塔潘','227 博塔斯']
listnba= [['哈登',78,36.8,36.1],['乔治',77,36.9,28.0],['阿德托昆博',72,32.8,27.7],['恩比德',64,33.7,27.5],['詹姆斯',55,35.2,27.4],['库里',69,33.8,27.3]]
listnum=[[2, 141, 126, 277, 323],[3, 241, 171, 404, 296],[1, 101, 128, 278, 123]]
print(max(listcha2,key=lambda x: x[-3:])) # 输出结果为：莱科宁 236，从字符串倒数第三位开始往后取数值
print(max(listcar))         # 输出结果为：[1181445, '卡罗拉']
print(max(listcar,key=lambda x:x[1]))   # 输出结果为：[789519, '高尔夫']
print(max(listnba,key=lambda x:x[3]))    #输出结果为： ['哈登', 78, 36.8, 36.1]
print(max(listnba,key=lambda x:(x[2],x[1],x[3])))  #输出结果为： ['乔治', 77, 36.9, 28.0]
print(max(listnba,key=lambda x:x[3]*x[1]))    #输出结果为： ['哈登', 78, 36.8, 36.1]
print(max(listnba,key=lambda x:(str(x[3]))[1:]))    #输出结果为：['乔治', 77, 36.9, 28.0]
print(max(listnum,key=lambda x:x[1]+x[2]+x[3]+x[4]))  #输出结果为：[3, 241, 171, 404, 296]
