# -*- coding: UTF-8 -*-

import cv2
import numpy as np
import matplotlib.pyplot as plt
from BrainDQN_Nature import BrainDQN


##################################################################################################################
##################################################################################################################

import random, pygame
from pygame.locals import *

FPS = 200 # 螢幕刷新率（在這裡相當於貪吃蛇的速度）
WINDOWWIDTH = 300 # 螢幕寬度
WINDOWHEIGHT = 300 # 螢幕高度
CELLSIZE = 20 # 小方格的大小
ALIVE_REWARD = 0 #-0.05   #存活獎勵
WIN_REWARD = 1    #獎勵
LOSE_REWARD = -1  #懲罰

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


# 神經網路的輸出
MOVE_STAY =  [1, 0, 0, 0, 0]
MOVE_UP   =  [0, 1, 0, 0, 0]
MOVE_DOWN =  [0, 0, 1, 0, 0]
MOVE_LEFT =  [0, 0, 0, 1, 0]
MOVE_RIGHT = [0, 0, 0, 0, 1]



class Game(object):
	def __init__(self):
		# 定義全域變數
		global FPSCLOCK, DISPLAYSURF, BASICFONT

		pygame.init() # 初始化pygame
		FPSCLOCK = pygame.time.Clock() # 獲得pygame時鐘
		DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) # 設置螢幕寬高
		BASICFONT = pygame.font.Font('freesansbold.ttf', 18) # BASICFONT
		pygame.display.set_caption('Greedy Snake') # 設置視窗的標題
		self.HEAD = 0 # syntactic sugar: index of the worm's head # 貪吃蛇的頭（）
		self.Bodylen=3
		#showStartScreen() # 顯示開始畫面
		self.runGame()
			
	def getRandomLocation(self): # 隨機生成一個座標位置  
	    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
													
	def runGame(self):
	    # 隨機初始化設置一個點作為貪吃蛇的起點
	    startx = random.randint(5, CELLWIDTH - 6)
	    starty = random.randint(5, CELLHEIGHT - 6)
	
	    # 以這個點為起點，建立一個長度為3格的貪吃蛇（陣列）
	    self.wormCoords = [{'x': startx, 'y': starty},
	                  {'x': startx - 1, 'y': starty},
	                  {'x': startx - 2, 'y': starty}]
	
	    self.direction = RIGHT # 初始化一個運動的方向   
	    self.apple = self.getRandomLocation() # 隨機一個apple的位置	
	
	# 根據 wormCoords 陣列繪製貪吃蛇
	def drawWorm(self,wormCoords):
	    for coord in wormCoords:
	        x = coord['x'] * CELLSIZE
	        y = coord['y'] * CELLSIZE
	        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
	        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
	        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
	        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)
	
	
	# 根據 coord 繪製 apple 
	def drawApple(self,coord):
	    x = coord['x'] * CELLSIZE
	    y = coord['y'] * CELLSIZE
	    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
	    pygame.draw.rect(DISPLAYSURF, RED, appleRect,8)
	
	# 繪製所有的方格 
	def drawGrid(self):
	    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
	        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
	    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
	        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))	

	def gen_action(self,optfromNN):
		if optfromNN[0]==1: return MOVE_STAY
		elif optfromNN[1]==1: return MOVE_UP
		elif optfromNN[2]==1: return MOVE_DOWN
		elif optfromNN[3]==1: return MOVE_LEFT
		elif optfromNN[4]==1: return MOVE_RIGHT
									
	def step(self, action):
		pygame.display.update()
		terminal=False
		reward=0
		
		if action==MOVE_LEFT and self.direction!=LEFT and self.direction!=RIGHT : self.direction = LEFT
		elif action==MOVE_RIGHT and self.direction!=LEFT and self.direction!=RIGHT : self.direction = RIGHT
		elif action==MOVE_UP and self.direction!=UP and self.direction!=DOWN: self.direction = UP
		elif action==MOVE_DOWN and self.direction!=UP and self.direction!=DOWN: self.direction = DOWN
		elif action==MOVE_STAY : pass

		# 檢查貪吃蛇是否撞到撞到邊界
		if self.wormCoords[self.HEAD]['x'] == -1 or self.wormCoords[self.HEAD]['x'] == CELLWIDTH or self.wormCoords[self.HEAD]['y'] == -1 or self.wormCoords[self.HEAD]['y'] == CELLHEIGHT:
			terminal=True
			reward=LOSE_REWARD
			print ("撞牆死....")
		
		for wormBody in self.wormCoords[1:]: # 檢查貪吃蛇是否撞到自己
			if wormBody['x'] == self.wormCoords[self.HEAD]['x'] and wormBody['y'] == self.wormCoords[self.HEAD]['y']:
				terminal=True
				reward=LOSE_REWARD
				print ("撞自己死....")
				break

		if terminal==False:
			# 檢查貪吃蛇是否吃到apple
			if self.wormCoords[self.HEAD]['x'] == self.apple['x'] and self.wormCoords[self.HEAD]['y'] == self.apple['y']:
				self.apple = self.getRandomLocation() # 重新隨機生成一個apple # 不移除蛇的最後一個尾巴格
				reward=WIN_REWARD
				self.Bodylen+=1
			else: #沒吃到apple也是要給予存活獎勵
				reward=ALIVE_REWARD/self.Bodylen
				del self.wormCoords[-1] # 移除蛇的最後一個尾巴格
	
			# 根據方向，添加一個新的蛇頭，以這種方式來移動貪吃蛇
			if self.direction == UP:
				newHead = {'x': self.wormCoords[self.HEAD]['x'], 'y': self.wormCoords[self.HEAD]['y'] - 1}
			elif self.direction == DOWN:
				newHead = {'x': self.wormCoords[self.HEAD]['x'], 'y': self.wormCoords[self.HEAD]['y'] + 1}
			elif self.direction == LEFT:
				newHead = {'x': self.wormCoords[self.HEAD]['x'] - 1, 'y': self.wormCoords[self.HEAD]['y']}
			elif self.direction == RIGHT:
				newHead = {'x': self.wormCoords[self.HEAD]['x'] + 1, 'y': self.wormCoords[self.HEAD]['y']}
			self.wormCoords.insert(0, newHead) # 插入新的蛇頭在陣列的最前面  

		#drawScore(len(self.wormCoords) - 3) # 繪製分數（分數為貪吃蛇陣列當前的長度-3）
		DISPLAYSURF.fill(BGCOLOR) # 繪製背景
		self.drawGrid()  # 繪製所有的方格
		self.drawWorm(self.wormCoords) # 繪製貪吃蛇
		self.drawApple(self.apple) # 繪製apple

		pygame.display.update() # 更新螢幕
		FPSCLOCK.tick(FPS) # 設置幀率
		
		if terminal==True:
			gameOverFont = pygame.font.Font('freesansbold.ttf', 40)
			gameOverSurf = gameOverFont.render('Game Over', True, WHITE)
			gameOverRect = gameOverSurf.get_rect()
			gameOverRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2-gameOverRect.height-10)
			DISPLAYSURF.blit(gameOverSurf, gameOverRect)
			
		# 獲得遊戲畫面的影像
		screen_image = pygame.surfarray.array3d(pygame.display.get_surface())
		pygame.display.update()
		# 返回遊戲畫面和對應的賞罰
		return screen_image,reward, terminal

##################################################################################################################
##################################################################################################################
									

# preprocess raw image to 80*80 gray image
def preprocess(observation):
	observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
	ret, observation = cv2.threshold(observation,1,255,cv2.THRESH_BINARY)
	#plt.imshow(observation, cmap ='gray'); plt.show();
	return np.reshape(observation,(80,80,1))

	
def playGame():
	# Step 0: Define reort
	win = 0
	lose = 0
	points = 0
	# Step 1: init BrainDQN
	actions = 5
	brain = BrainDQN(actions)
	# Step 2: init Game
	bg = Game()
	# Step 3: play game
	# Step 3.1: obtain init state
	action0 = bg.gen_action([1,0,0,0,0])  # do nothing
	observation0, reward0, terminal = bg.step(action0)
	observation0 = cv2.cvtColor(cv2.resize(observation0, (80, 80)), cv2.COLOR_BGR2GRAY)
	ret, observation0 = cv2.threshold(observation0,1,255,cv2.THRESH_BINARY)
	brain.setInitState(observation0)

	# Step 3.2: run the game
	while True:
		pygame.event.get()  #讓遊戲畫面能夠更新
		action = bg.gen_action(brain.getAction())
		Observation,reward,terminal = bg.step(action)
		nextObservation = preprocess(Observation)
		brain.setPerception(nextObservation,action,reward,terminal)
		
		########################  統計輸出報表用  ########################
		points+=reward
		if terminal==True: 
			win+=points
			lose+=1
			points=0
			bg = Game()
		print("Lost cnt:" ,lose," ,win_points:",round(points,2)," ,cnt:",brain.timeStep)
		if brain.timeStep % 1000 == 0:
			learn_rate.append(lose)
			win_cnt.append(win)
			plt.plot(learn_rate,"g");plt.plot(win_cnt,"r");plt.show();
			lose=0
			win=0
		########################  統計輸出報表用  ########################

		
learn_rate=[]
win_cnt=[]
def main():
	playGame()
	
if __name__ == '__main__':
	main()


#	# 繪製分數        
#	def drawScore(self,score):
#	    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
#	    scoreRect = scoreSurf.get_rect()
#	    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
#	    DISPLAYSURF.blit(scoreSurf, scoreRect)				
				
# 顯示遊戲結束畫面
#	def showGameOverScreen():
#	    gameOverFont = pygame.font.Font('freesansbold.ttf', 50)
#	    gameSurf = gameOverFont.render('Game', True, WHITE)
#	    overSurf = gameOverFont.render('Over', True, WHITE)
#	    gameRect = gameSurf.get_rect()
#	    overRect = overSurf.get_rect()
#	    gameRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2-gameRect.height-10)
#	    overRect.midtop = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
#	
#	    DISPLAYSURF.blit(gameSurf, gameRect)
#	    DISPLAYSURF.blit(overSurf, overRect)
#	    drawPressKeyMsg()
#	    pygame.display.update()
#	    pygame.time.wait(500)
#	    checkForKeyPress() # clear out any key presses in the event queue
#	
#	    while True:
#	        if checkForKeyPress():
#	            pygame.event.get() # clear event queue
#	            return
				
				#    while True: 
#
#        # 這裡一直迴圈於開始遊戲和顯示遊戲結束畫面之間，
#        # 運行遊戲裡有一個迴圈，顯示遊戲結束畫面也有一個迴圈
#        # 兩個迴圈都有相應的return，這樣就可以達到切換這兩個模組的效果
#
#        runGame() # 運行遊戲
#
#        showGameOverScreen() # 顯示遊戲結束畫面

#		for event in pygame.event.get(): # 事件處理
#			if event.type == QUIT: # 退出事件
#				terminate()
#			elif event.type == KEYDOWN: # 按鍵事件
#				#如果按下的是左鍵或a鍵，且當前的方向不是向右，就改變方向，以此類推
#				if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
#					direction = LEFT
#				elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
#					direction = RIGHT
#				elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
#					direction = UP
#				elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
#					direction = DOWN
#				elif event.key == K_ESCAPE:
#					terminate()


#	# 繪製提示消息        
#	def drawPressKeyMsg():
#	    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
#	    pressKeyRect = pressKeySurf.get_rect()
#	    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
#	    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)        
#	
#	# 檢查按鍵是否有按鍵事件
#	def checkForKeyPress():
#	    if len(pygame.event.get(QUIT)) > 0:
#	        terminate()
#	
#	    keyUpEvents = pygame.event.get(KEYUP)
#	    if len(keyUpEvents) == 0:
#	        return None
#	    if keyUpEvents[0].key == K_ESCAPE:
#	        terminate()
#	    return keyUpEvents[0].key
	
#	# 顯示開始畫面
#	def showStartScreen():
#	
#	    DISPLAYSURF.fill(BGCOLOR)
#	    titleFont = pygame.font.Font('freesansbold.ttf', 50)
#	    titleSurf = titleFont.render('Greedy Snake', True, GREEN)
#	    titleRect = titleSurf.get_rect()
#	    titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
#	    DISPLAYSURF.blit(titleSurf, titleRect)
#	    drawPressKeyMsg()
#	
#	    pygame.display.update()
#	
#	    while True:
#	
#	        if checkForKeyPress():
#	            pygame.event.get() # clear event queue
#	            return
	
	
#	# 退出
#	def terminate():
#	    pygame.quit()
#	    sys.exit()
