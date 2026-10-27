# def get_index():
#     index_list = [i for i, j in enumerate(res) if j == '-----']
#     return index_list
def initialize(filename:str):
    print("***************正在初始化***************")
    global res
    res = []
    with open(filename, "r",encoding = 'utf-8') as f:
        print("*************读取到配置文件*************")
        for line in f.readlines():
            line = line.strip('\n')
            res.append(line)
    print("***************初始化成功***************")
    return res


def ans(num: int):
    index_list = [i for i, j in enumerate(res) if j == '-----']
    try:
        index_i = index_list[num - 1] + 1
        index_j = index_list[num]
        for _ in res[index_i:index_j]:
            print(_)

    except TypeError:
        print('您输入的题目序号有误，请重新输入正确的题目序号！')
    except IndexError:
        print("您输入的题号超出题目数量，请检查！")
    except BaseException:
        print('请输入正确的题目序号！')

def hint(num: int):
    index_list = [i for i, j in enumerate(res) if j == '-----']
    try:
        index_i = index_list[num - 1] + 1
        index_j = index_list[num]
        for _ in res[index_i:index_j]:
            print(_)

    except TypeError:
        print('您输入的题目序号有误，请重新输入正确的题目序号！')
    except IndexError:
        print("您输入的题号超出题目数量，请检查！")
    except BaseException:
        print('请输入正确的题目序号！')