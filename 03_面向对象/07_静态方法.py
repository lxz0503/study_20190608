# 在类的内部，如果有以下特征
# 不需要访问实例属性或者是调用实例方法；理解为没有参数
# 也不需要访问类属性或者调用类方法。
# 那么就可以把这个方法封装成静态方法。
# 静态方法需要用@staticmethod来表示。
# 使用静态方法------   在类的外部用  类名.调用静态方法
# 在类的内部，其他方法依然可以调用静态方法 self.静态方法

class Game(object):
    # 历史最高分
    top_score = 0

    def __init__(self, player_name):
         self.player_name = player_name

    @staticmethod     # 一般一些帮助信息或者如何使用函数的封装为静态方法
    def show_help():
        print("帮助信息，让僵尸进入大门")

    @classmethod
    def show_top_score(cls):
        print("历史记录%d" % cls.top_score)

    def start_game(self):
        self.show_top_score() # 在类内部，实例方法可以调用类方法  self.类方法
        self.show_help()   # 在类内部，其他方法可以调用静态方法  self.静态方法
        print("%s开始游戏了，冲啊" % self.player_name)

# 1.查看游戏的帮助信息, 调用静态方法
Game.show_help()
# 2.查看历史最高分    # 在类的外部访问类方法
Game.show_top_score()    #
# 3.创建游戏对象,访问实例属性和实例方法
obj = Game("小猪猪")
obj.start_game()