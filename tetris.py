import random
import math
from time import sleep

def tetris():
	GAMETYPE = ['random','console']
		#Types: manual , random
		#		console, file
	#Game constants
	gameUpdateRate = .1 #seconds between frames

	global SCORE

	SCORE=0

	#Field width and height
	global w, h
	w, h = 10, 12

	#Symbols
	global empty, fill, active
	empty = '-'
	fill = '0'
	active = '@'

	global frozeSym,hitSym,moveSym
	frozeSym='#'
	hitSym='!'
	moveSym='~'

	# ~~~~~ Tetrinos
	global blocks
	global sqr_block
	
	s_block = [[-1,1],[0,1],[0,0],[1,0]]
	z_block = [[-1,2],[0,0],[0,1],[0,2]]
	sqr_block = [[0,0],[1,0],[0,1],[1,1]]
	li_block = [[-1,0],[0,0],[1,0],[2,0]]
	t_block = [[-1,0],[0,0],[1,0],[0,1]]
	l_l_block = [[-1,0],[-1,1],[0,1],[1,1]]
	l_r_block =  [[1,0],[-1,1],[0,1],[1,1]]

	blocks = [s_block,s_block,
				sqr_block,li_block,t_block,
				l_l_block,l_r_block]
	# ~~~~~~~~

	#Create field
	staticField = [None]*h
	for i in range(h):
		staticField[i]=[empty]*10

	#Create block
	activeBlock = Tetrino()
	firstFrame = True

	#----------------
	#---- Game Loop -
	#----------------
	frameCommand = ''
	while 1:
		# FOR READING/WRITNG FILE
		# file open
		# read strings into 2d array
		#Random input
		if GAMETYPE[0] == 'random':
			inputs = 'aqlpd'
			frameCommand=''
			inputStringLen = int(math.sqrt(random.randrange(100)))
			for _ in range(inputStringLen):
				newCommand = inputs[random.randrange(len(inputs))]
				frameCommand = frameCommand+newCommand
		for charac in frameCommand:
			if charac == 'l': activeBlock.moveInX(1, staticField)
			elif charac == 'a': activeBlock.moveInX(-1, staticField)
			elif charac == 'p': activeBlock.rotate('cw',staticField)
			elif charac == 'q': activeBlock.rotate('ccw',staticField)
			elif charac == 'd': activeBlock.moveDown(1, staticField)
			elif charac == 'D': 
				activeBlock.moveDown(h, staticField)
				activeBlock.state = 'froze'

		if not firstFrame: activeBlock.update(staticField)
		else: firstFrame=False

		#If active block is frozen, add to static field
		if activeBlock.state == 'froze':
			#Check for game over
				#frozen tetrino is overlapping
			if checkForFailure(staticField,activeBlock):
				print 'Game over. Score: {}'.format(SCORE)
				return

			staticField=updateField(staticField,activeBlock)
			staticField=clearLines(staticField)
			activeBlock = Tetrino()

		dynamicField = updateField(staticField,activeBlock)
			
		#print field to console
		if SCORE > 999: SCORE=999
		print 'Score: {}'.format(SCORE)
		printField(dynamicField)
			#status line
			# move/hit/froze, x pos, y pos, shape, rotation
		print bottomStatusLine(activeBlock)

		#wait a 'frame'
		sleep(gameUpdateRate)
		if GAMETYPE[0] == 'manual':
			frameCommand=raw_input('Input:  ')
		#wait for input
		#frameCommand = raw_input('Input: ')

################## CLASSES #################
class Tetrino:
	state = 'move' # 'froze' 'hit'
	rotation = 0
	def __init__(self):
		#Define shape
		self.blockNdx = random.randrange(len(blocks))
		self.shape = list(blocks[self.blockNdx])
		#spawn at top of board
		self.x = 4
		self.y = 0
	def update(self,field):
		#Check collision
		self.moveDown(1,field)
	def moveDown(self,move,field):
		for _ in range(move):
			if not self.collisionBelow(1,field) and self.state == 'move':
				self.y+=1
			else: 
				self.collideBelow()
				return
	def rotate(self,direc,field):
		#direc = cw, ccw
		if self.shape == sqr_block: return
		newShape = []
		rot = 0
		for i in range(len(self.shape)):
			curX=self.shape[i][0]
			curY=self.shape[i][1]
			if direc=='cw':
				newX=-curY
				newY=curX
				rot=-1
			elif direc=='ccw':
				newX=curY
				newY=-curX
				rot=1

			newShape.append([newX,newY])
		if not self.collisionAnywhere(newShape,field):
			for i in range(len(newShape)):
				self.shape[i] = newShape[i]
			self.state = 'move'
			self.rotation+=rot
			if self.rotation <0: self.rotation+=4
			elif self.rotation >3: self.rotation-=4

	def collisionAnywhere(self,block,field):
		for b in block:
			if self.x+b[0] >= w or self.x+b[0] < 0:
				return True
			elif self.y+b[1] >= h:
				return True
			elif self.x+b[0] >=0 and self.x+b[0]<w and self.y+b[1] >0:
				if field[self.y+b[1]][self.x+b[0]]==fill:
					return True
		return False

	def moveInX(self,move,field):
		if move == 0: return
		#inc is -1,1
		inc = move/abs(move)
		for _ in range(abs(move)):
			if not self.collisionSide(inc,field):
				self.x += inc
				self.state='move'
	def collisionSide(self,move,field):
		for block in self.shape:
			#Get pos of block
			blockx = self.x+block[0]
			blocky = self.y+block[1]
			#check if at bottom
			if blockx+move == w or blockx+move == -1:
				return True
			#check if above solid block
			elif field[blocky][blockx+move] == fill:
				return True
		return False
	def collisionBelow(self,move,field):
		#Check collision below
		for block in self.shape:
			#Get pos of block
			blockx = self.x+block[0]
			blocky = self.y+block[1]+move
			#check if at bottom
			if blocky == h:
				return True
			#check if above solid block
			elif blocky < h and blocky>=0: 
				if field[blocky][blockx] == fill:
					return True
		return False
	def collideBelow(self):
		if self.state=='move': self.state='hit'
		elif self.state=='hit': 
			self.state='froze'
	

################# FUNCTIONS ################
def bottomStatusLine(block):
	global moveSym, hitSym, frozeSym
	statusLine=''
	#Active block status
	if block.state=='move':
		statusLine = statusLine+moveSym
	elif block.state=='hit':
		statusLine = statusLine+hitSym
	elif block.state=='froze':
		statusLine = statusLine+frozeSym

	#x coord
	statusLine = statusLine+' {}'.format(block.x)
	#y coord
	statusLine = statusLine+' {}'.format(block.y)
	#shape ndx
	statusLine = statusLine+' {}'.format(block.blockNdx)
	
	return statusLine+'{}'.format(block.rotation)

def clearLines(field):
	global SCORE

	rowsToClear=[]
	for i in range(len(field)):
		if field[i] == [fill]*w:
			#clear out row... hmm
			rowsToClear.append(i)
			SCORE += 1

	#And here we construct a new field!
	offset = 0
	outField=[]
	for i in range(len(field)+len(rowsToClear)):
		if i < len(rowsToClear):
			outField.append([empty]*w)
			offset +=1
		elif i-offset in rowsToClear:
			next
		else:
			outField.append(field[i-offset])
	return outField

	#Updates field with block position
def updateField(field,block):
	#Welp, gotta do this to copy over static field without editing it
	outField = []
	for i in range(h):
		outField.append([])
		for j in range(w):
			outField[i].append(field[i][j])
			
	#Draw field with block
	if block.state == 'froze': blockSym = fill
	else: blockSym = active

	for coord in block.shape:
		row =block.y+coord[1]
		col = block.x+coord[0]
		if row>=0 and row<=h-1:
			if outField[row][col]!=fill:
				outField[row][col]=blockSym
	return outField
	
def checkForFailure(field,block):
	for coord in block.shape:
		blockx = block.x+coord[0]
		blocky = block.y+coord[1]
		if blockx >=0 and blockx < w and blocky >=0:
			if field[blocky][blockx]==fill:
				return True
	return False
		
	# Prints field to console
def printField(field):
	for i in range(len(field)):
		row = ''
		for j in range(len(field[i])):
			row = row+field[i][j]
		print row

################## Main function ###########
if __name__ == '__main__':
	tetris()
