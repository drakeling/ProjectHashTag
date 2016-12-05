#!/usr/bin/python
# #.py Version 0.1
# By: Daniel McLaughlin
#
# This is a game that uses simple data mining to create an experience for the player
# to explore. The player may move between open walls (or not!) to explore rooms
# that draw descriptions from tweets pertaining to a unifying theme of a trending topic.
# Each room decides its open walls through the hashify function, that reduces the tweet
# to a single value.
# This dungeon crawler is the first iteration of games to be built on this #GameEngine

import twitter
import random
import sys

""" Variables for the #GameEngine credentials - Provide Twitter API credentials here"""
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

# Hashing function for string of text. We get an end value by taking the sum of each
# character from text, after multiplying it by 65537, and then modulus the max parameter
# to satisfy whatever outcome we're looking for.
def hashify(text, max):
	hash_val = max
	for c in text:
		cur = ord(c)
		hash_val += (cur * 65537)
	return hash_val % max

# For writing the title of the game, which should always have a single # before it
def hashtagify(title):
	ret_title = "#"
	if (title[0].encode('ascii', 'ignore') == '#'):
		title = title[1:len(title)]
	ret_title += title
	return ret_title

# For writing our introduction to the game
def getIntro(title, number):
	intro = gameOpens[number]
	intro = intro.replace("#", title.encode('ascii', 'ignore'))
	print intro
	

# These four functions are for a set of values that represent walls
northWalls	= [1, 5, 6, 7, 12, 13, 14, 15]
eastWalls	= [2, 5, 8, 9, 11, 13, 14, 15]
southWalls	= [3, 6, 8, 10, 11, 12, 14, 15]
westWalls	= [4, 7, 9, 10, 11, 12, 13, 15]

def getNorth(walls):
	if walls in northWalls:
		return 1
	else:
		return 0
		
def getEast(walls):
	if walls in eastWalls:
		return 1
	else:
		return 0
		
def getSouth(walls):
	if walls in southWalls:
		return 1
	else:
		return 0
		
def getWest(walls):
	if walls in westWalls:
		return 1
	else:
		return 0

# Quick function for parsing numbers out of strings
def representsInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

# Quick function to get the absolute value
def abs(i):
    if (i < 0):
        return i * -1
    else:
        return i

# Some different ways to introduce the game
gameOpens = [
	"Welcome to the exhibit of # \nYou are amoung all the artifacts saved from\nthat time. Feel free to explore!\n\n",
	"You find yourself inside an unfamiliar land\nand all you can think about is #\n\n",
	"# \n\n",
	"You wake up, feeling faint and weak. You gaze up in the dimly lit room.\nYou see an inscription on the wall, which reads # \n\n"
]

# Some different ways to introduce rooms
roomOpens = [ 
	"You stumble into this room\n",
	"Without knowing it, you found yourself here\n",
	"You wander for what seems like forever\n",
	"Coming through the door, you find this!\n",
	"You're only a little dizzy after that last room\n"
]

			
# Creating a room class for v 0.1, The Dungeon iteration of #
class dungeonRoom:
	"""Rooms are the environments that players will interact in, which will
	each have data generated from tweets pertaining to the trend choosen at random"""
	def __init__(self, tweet = "Missing Description", walls = 0):
		self.tweet = tweet.encode('ascii', 'ignore')
		self.walls = walls
		self.north = getNorth(walls)
		self.east = getEast(walls)
		self.south = getSouth(walls)
		self.west = getWest(walls)
	
	def debugRoom(self):
		print self.tweet
		print "Wall Data: %s %s %s %s" % (self.north, self.east, self.south, self.west)
		print "============="
	
	def printRoom(self):
		print random.choice(roomOpens)
		print self.tweet
		print ("\nObvious exits are: "),
		self.printDirs()
	
	def firstPrintRoom(self):
		print self.tweet
		print ("\nObvious exits are: "),
		self.printDirs()
	
	def printDirs(self):
		if (self.north == 0):
			print ("North "),
		if (self.east == 0):
			print ("East "),
		if (self.south == 0):
			print ("South "),
		if (self.west == 0):
			print ("West "),
		if (self.north == 1 and self.east == 1 and self.south == 1 and self.west == 1):
			print ("Nowhere!"),
		print ""
	
	# Returns if there's a wall in the way or not
	def checkWall(self, dir):
		if (dir == 'n' and self.north == 0):
			return 0
		elif (dir == 'e' and self.east == 0):
			return 0
		elif (dir == 's' and self.south == 0):
			return 0
		elif (dir == 'w' and self.west == 0):
			return 0
		else:
			return 1

""" Some objects needed to start data mining"""
twitter_api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
trends = twitter_api.GetTrendsCurrent()
search = []
dungeon = []

# Keep searching trends until we find one with 25 search results
while (len(search) < 25):
	t = random.choice(trends)
	search = twitter_api.GetSearch(t.name, count = 25)

# Building a 5x5 dungeon with random wall configurations from tweets
for s in search:
	cur = dungeonRoom(s.text, hashify(s.text, 16))
	dungeon.append(cur)

# Beginning the game!
title = hashtagify(t.name)
getIntro(title, hashify(t.name, len(gameOpens)))

# Choosing a random room to begin
curRoom = random.choice(dungeon)
first = 1

while True:
	# Dungeon crawling variables
	roomNum = dungeon.index(curRoom)
	curX = roomNum / 5
	curY = roomNum % 5
	if (first == 0):
		curRoom.printRoom()
	else:
		curRoom.firstPrintRoom()
		first = 0
	
	player = raw_input('Your map reads: (%s, %s)\nWhere do you go?\n: ' % (curX, curY))
	player = player.lower().split(" ")
	
	""" Decide if the player can move or not. There can't be a wall in the way,
		And we have need to wrap around if we go outside dungeon indices """
	if player[0] in ['n', 'north']:
		if (curRoom.checkWall('n') == 0):
			newX = (curX + 1) % 5
			newIndex = (newX * 5) + curY
			curRoom = dungeon[newIndex]
			print "You go north\n\n"
		else:
			print "There's no path north\n\n"
			first = 1
	elif player[0] in ['e', 'east']:
		if (curRoom.checkWall('e') == 0):
			newY = (curY + 1) % 5
			newIndex = (curX * 5) + newY
			curRoom = dungeon[newIndex]
			print "You go east\n\n"
		else:
			print "There's no path east\n\n"
			first = 1
	elif player[0] in ['s', 'south']:
		if (curRoom.checkWall('s') == 0):
			newX = (curX - 1)
			if (newX == -1):
				newX = 4
			newIndex = (newX * 5) + curY
			curRoom = dungeon[newIndex]
			print "You go south\n\n"
		else:
			print "There's no path south\n\n"
			first = 1
	elif player[0] in ['w', 'west']:
		if (curRoom.checkWall('w') == 0):
			newY = (curY - 1)
			if (newY == -1):
				newY = 4
			newIndex = (curX * 5) + newY
			curRoom = dungeon[newIndex]
			print "You go west\n\n"
		else:
			print "There's no path west\n\n"
			first = 1
	elif player[0] in ['debug']:
		curRoom.debugRoom()
	elif player[0] in ['exit']:
		print "Don't forget %s!" % title
		sys.exit(0)
	elif player[0] in ['teleport', 'warp']:
		if (representsInt(player[1]) and representsInt(player[2])):
			newX = abs(int(player[1])) % 5
			newY = abs(int(player[2])) % 5
			newIndex = (newX * 5) + newY
			curRoom = dungeon[newIndex]
		else:
			print "You %sed!\n\n" % player[0]
			print "I didn't understand...\n\n"
			first = 1
	else:
		print "I didn't understand...\n\n"
		first = 1