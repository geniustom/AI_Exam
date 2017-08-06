# -*- coding: UTF-8 -*-
'''
Created on 2017年1月7日

@author: 小峰峰
'''

import random, sys, time, pygame
from pygame.locals import *

FPS = 5 # 螢幕刷新率（在這裡相當於貪吃蛇的速度）
WINDOWWIDTH = 450 # 螢幕寬度
WINDOWHEIGHT = 450 # 螢幕高度
CELLSIZE = 15 # 小方格的大小

# 斷言，螢幕的寬和高必須能被方塊大小整除
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

# 橫向和縱向的方格數
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)


# 定義幾個常用的顏色
# R G B
WHITE = (255, 255, 255)
BLACK = ( 0, 0, 0)
RED = (255, 0, 0)
GREEN = ( 0, 255, 0)
DARKGREEN = ( 0, 155, 0)
DARKGRAY = ( 40, 40, 40)
BGCOLOR = BLACK

# 定義貪吃蛇的動作
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# 貪吃蛇的頭（）
HEAD = 0 # syntactic sugar: index of the worm's head



def main():

    # 定義全域變數
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init() # 初始化pygame
    FPSCLOCK = pygame.time.Clock() # 獲得pygame時鐘
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) # 設置螢幕寬高
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18) # BASICFONT
    pygame.display.set_caption('Greedy Snake') # 設置視窗的標題

    showStartScreen() # 顯示開始畫面

    while True: 

        # 這裡一直迴圈於開始遊戲和顯示遊戲結束畫面之間，
        # 運行遊戲裡有一個迴圈，顯示遊戲結束畫面也有一個迴圈
        # 兩個迴圈都有相應的return，這樣就可以達到切換這兩個模組的效果

        runGame() # 運行遊戲

        showGameOverScreen() # 顯示遊戲結束畫面


def runGame():
    # 隨機初始化設置一個點作為貪吃蛇的起點
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)

    # 以這個點為起點，建立一個長度為3格的貪吃蛇（陣列）
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]


    direction = RIGHT # 初始化一個運動的方向

    # 隨機一個apple的位置
    apple = getRandomLocation()


    while True: # 遊戲主迴圈
        for event in pygame.event.get(): # 事件處理
            if event.type == QUIT: # 退出事件
                terminate()
            elif event.type == KEYDOWN: # 按鍵事件
                #如果按下的是左鍵或a鍵，且當前的方向不是向右，就改變方向，以此類推
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()



        # 檢查貪吃蛇是否撞到撞到邊界
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over

        
        for wormBody in wormCoords[1:]: # 檢查貪吃蛇是否撞到自己
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # 檢查貪吃蛇是否吃到apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            apple = getRandomLocation() # 重新隨機生成一個apple # 不移除蛇的最後一個尾巴格
        else:
            del wormCoords[-1] # 移除蛇的最後一個尾巴格

        # 根據方向，添加一個新的蛇頭，以這種方式來移動貪吃蛇
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        wormCoords.insert(0, newHead) # 插入新的蛇頭在陣列的最前面     
        DISPLAYSURF.fill(BGCOLOR) # 繪製背景
        drawGrid()  # 繪製所有的方格
        drawWorm(wormCoords) # 繪製貪吃蛇
        drawApple(apple) # 繪製apple
        drawScore(len(wormCoords) - 3) # 繪製分數（分數為貪吃蛇陣列當前的長度-3）
        pygame.display.update() # 更新螢幕
        FPSCLOCK.tick(FPS) # 設置幀率

# 繪製提示消息        
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)        

# 檢查按鍵是否有按鍵事件
def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

# 顯示開始畫面
def showStartScreen():

    DISPLAYSURF.fill(BGCOLOR)
    titleFont = pygame.font.Font('freesansbold.ttf', 50)
    titleSurf = titleFont.render('Greedy Snake', True, GREEN)
    titleRect = titleSurf.get_rect()
    titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
    DISPLAYSURF.blit(titleSurf, titleRect)
    drawPressKeyMsg()

    pygame.display.update()

    while True:

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


# 退出
def terminate():
    pygame.quit()
    sys.exit()

# 隨機生成一個座標位置    
def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

# 顯示遊戲結束畫面
def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 50)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2-gameRect.height-10)
    overRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

# 繪製分數        
def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


# 根據 wormCoords 陣列繪製貪吃蛇
def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


# 根據 coord 繪製 apple 
def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

# 繪製所有的方格 
def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()

