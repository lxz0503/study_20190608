# C:\Users\Administrator\.PyCharm2018.2\system\python_stubs\-643338342\pygame
# above dir is the implementation
import pygame
pygame.init()
# 创建游戏窗口 480*20
screen = pygame.display.set_mode((480, 700))
# 绘制背景图像
# 1 加载背景图像
bg = pygame.image.load("./images/background.png")
# 2 绘制背景图像
screen.blit(bg, (100, 100))
# 3 显示背景图像
pygame.display.update()
while True:
    pass

pygame.quit()