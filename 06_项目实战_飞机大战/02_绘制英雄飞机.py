# C:\Users\Administrator\.PyCharm2018.2\system\python_stubs\-643338342\pygame
# above dir is the implementation
import pygame
from plane_sprites import *
pygame.init()
# 创建游戏窗口 480*20
screen = pygame.display.set_mode((480, 700))
# 绘制背景图像
bg = pygame.image.load("./images/background.png")
screen.blit(bg, (100, 100))

# 绘制英雄的飞机
hero = pygame.image.load("./images/me1.png")
screen.blit(hero, (150, 500))

# 在所有绘制工作完成后，同时调用update方法，产生一帧，frame
# 要产生高品质动画，需要每秒调用60次帧
pygame.display.update()
# 创建一个时钟对象
clock = pygame.time.Clock()
# 定义rect记录飞机的初始位置, 创建一个对象
hero_rect = pygame.Rect(150, 400, 102, 126)


# 精灵演练，创建敌机的精灵
enemy = GameSprite("./images/enemy1.png")
enemy1 = GameSprite("./images/enemy1.png", 2)
# 创建敌机的精灵组
enemy_group = pygame.sprite.Group(enemy, enemy1)

while True:
    # 制定循环体内部代码执行的频率，如下是每秒60帧，即屏幕刷新频率
    clock.tick(60)
    # 捕获事件,返回一个列表
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("退出游戏")
            pygame.quit()
            exit()
    # 修改飞机位置
    hero_rect.y -= 1
    # 判断飞机位置,底部飞出边界后回到出发位置
    if hero_rect.bottom <= 0:
        hero_rect.y = 700
    # 调用blit方法绘制图像
    screen.blit(bg, (0, 0))
    screen.blit(hero, hero_rect)

    # 让精灵组调用两个方法
    enemy_group.update()   # 让组中的所有精灵更新位置
    enemy_group.draw(screen)  # 把所有精灵绘制在屏幕上

    # 调用update方法更新显示
    pygame.display.update()
pygame.quit()