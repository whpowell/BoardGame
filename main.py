import pygame
import math
import os
import hex
from random import shuffle
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

class BoardGame(ConnectionListener):
	
	def __init__(self):				
		#init pygame get screen resolution set backgroud white
		pygame.init()
		self.resl = pygame.display.Info()
		self.background_colour = (255,255,255)	
		
		#load images
		self.initGraphics()
	
		#init clock
		self.clock=pygame.time.Clock()	

		#connect to server			
		address = raw_input("Address of Server: ")
		try:
			if not address:
				host, port="localhost", 8000
			else:
				host, port=address.split(":")
			self.Connect((host,int(port)))
		except:
			print "Error Connecting to Server"
			print "Usage:", "host:port"
			print "e.g.", "localhost:31425"
			exit()
		print "Board Game client started"
		
		#listen for server communication
		self.running = False
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)
			
		#player 0 starts
		if self.num == 0:
			self.turn = True
		else:
			self.turn = False
			
		#display screen	
		self.screen = pygame.display.set_mode((self.resl.current_w, self.resl.current_h))
		pygame.display.set_caption("Board Game")
		self.screen.fill(self.background_colour)

		self.initHexgrid()
		
		#initialise players
		self.players = []
		for i in range(self.number_players):
			if i == self.num:
				self.players.append(Player(5,5))
			else:
				self.players.append(Player(self.resl.current_w-205,5+250*(((self.num-i)%self.number_players)-1)))
			
		#keep track of recent clicks and cursor hover action
		self.justclicked = 10
		self.overAction = False
		self.playing_card = False
		self.played_block_hex = False
		self.played_block_hex_pos = []
		self.place_extra_hex = False
		self.round_number = 0

		self.place_range = 1

		self.skip_button = Button("skip card phase?",self)

		self.action_switcher = { 

				"choose primary race":self.choosePrimaryRace,
				"choose secondary race":self.chooseSecondaryRace,
				"remove hexagon":self.removeHexagon,
				"block hexagon":self.blockHexagon,
				"place hexagon":self.placeHexagon,
				"play card":self.playCard,
				"take card":self.takeCard,
				"choose move":self.chooseMove,			
				"choose opponent card":self.chooseOpponentCard

				}

	def initHexgrid(self):
		self.hexgrid = hex.Hexgrid(round((self.resl.current_w-400)/30),350,150,self.screen)
		self.hexgrid.sethextypes([[1,5],[2,4],[2,5],[4,8],[5,1],[5,8],[6,1],[6,9],[11,0],[12,5],[11,6],[12,4]],"terr")
		self.hexgrid.sethextypes([[0,9],[1,2],[1,7],[1,8],[2,2],[2,7],[3,2],[4,3],[4,6],[5,3],[5,4],[5,5],[6,4],[6,5],[6,6],[7,3],[7,4],[7,5],[7,6],[8,2],[8,3],[8,4],[8,5],[8,7],[8,8],[9,1],[9,3],[9,6],[9,7],[10,3],[10,4],[10,8],[12,2],[12,8],[12,9],[13,1],[13,8],[14,0],[14,1],[14,2]],"score")

		
	def initGraphics(self):
		#load images from folder
		
		#load playable cards and races
		self.card_images = []
		self.primary_race_images = []
		self.secondary_race_images = []
		for k in range(13):
			for i in os.listdir("BGHackathon"):
				if i.startswith("CARD") and i.endswith("%02d.jpg"%k):
					self.card_images.append(pygame.image.load("BGHackathon/"+i))
			
		for i in range (6):
			self.primary_race_images.append(pygame.image.load("BGHackathon/RACEprimary%r.jpg"%i))
			self.secondary_race_images.append(pygame.image.load("BGHackathon/RACEsecondary%r.jpg"%i))
				
		self.card_back = pygame.image.load("BGHackathon/CARDback.jpg")
		
		#intitialise text
		self.largeText = pygame.font.Font('freesansbold.ttf',40)
		self.redindicator = pygame.image.load("BGHackathon/redindicator.png")
		self.greenindicator = pygame.image.load("BGHackathon/greenindicator.png")

		self.take_deck_pos = Rect(10,400,300,200)
		self.discard_deck_pos = Rect(250,400,300,200)

		self.enlarge_rect = Rect(400,200,500,350)
				
	def drawBoard(self):
		#draw board at screen resolution
		self.hexgrid.draw_hexgrid()
		
	def drawPlayerCards(self):

		for player in self.players:
			player.hand_rect_array.draw(self.makeList(self.card_images,player.hand),self.screen)

			if player.hand_rect_array.overRectArray(self.x,self.y):
				player.hand_rect_array.enlarge(self.card_images[player.hand[player.hand_rect_array.overWhichRect(self.x,self.y)]],self.screen)
												
	def drawDecks(self):
		self.screen.blit(pygame.transform.scale(self.card_back, [self.take_deck_pos.w,self.take_deck_pos.h]),[self.take_deck_pos.x,self.take_deck_pos.y])
		
	def drawHUD(self):
		self.rounds_rmn = 24-2*self.number_players - self.round_number
		label = self.largeText.render("Rounds remaining: %r"%self.rounds_rmn,1,(0,0,0))
		self.screen.blit(label,(400,10))
		if self.turn:
			self.screen.blit(self.greenindicator,(300,10))
		else:
			self.screen.blit(self.redindicator,(300,10))

	def resolveAction(self,x,y):
		return self.action_switcher[self.action](x,y)

	def resolveCard(self,card):
		
		self.playing_card = True

		if card == 0:
			self.action = "choose opponent"

		elif card == 1:
			self.action = "place hexagon"
			self.place_range = 20
			self.place_type = "normal"

		elif card == 2:
			self.action = "place hexagon"
			self.place_range = 1
			self.place_type = "score"

		elif card == 3:
			self.action = "choose opponent card"

		elif card == 4:
			self.action = "block hexagon"

		elif card == 5:
			self.action = "move hexagon"

		elif card == 6:
			self.action = "remove hexagon"
			self.attack_value = 1
			
		elif card == 7:
			self.action = "remove hexagon"
			self.attack_value = 2

		elif card == 8:
			self.action = "remove hexagon"
			self.attack_value = 3			

		elif card == 9:
			self.action = "place hexagon"
			self.place_range = 1
			self.place_type = "normal"
			self.place_extra_hex = True

		elif card == 10:
			self.action = "capture hexagon"
			self.attack_value = 1

		elif card == 11:
			self.action = "capture hexagon"
			self.attack_value = 2

		elif card == 12:
			self.action = "capture hexagon"
			self.attack_value = 3

	def makeList(self,list1,list2):
		list=[]
		for i in list2:
			list.append(list1[i])
		return list

	def choosePrimaryRace(self,x,y):
		self.primary_race_rect_array.draw(self.makeList(self.primary_race_images,self.primary_races),self.screen)
		if self.primary_race_rect_array.overRectArray(x,y):
			self.primary_race_rect_array.enlarge(self.primary_race_images[self.primary_races[self.primary_race_rect_array.overWhichRect(x,y)]],self.screen)
			if self.turn:
				self.overAction = True
				if self.clicked():
					self.Send({"action":"talk","player action":"choose primary race","chosen race":self.primary_races[self.primary_race_rect_array.overWhichRect(x,y)],"playerid":self.num,"gameid":self.gameid})
					self.justclicked = 10
					self.wait()
					self.endTurn()


	def chooseSecondaryRace(self,x,y):
		self.secondary_race_rect_array.draw(self.makeList(self.secondary_race_images,self.secondary_races),self.screen)
		if self.secondary_race_rect_array.overRectArray(x,y):
			self.overAction = True
			self.secondary_race_rect_array.enlarge(self.secondary_race_images[self.secondary_races[self.secondary_race_rect_array.overWhichRect(x,y)]],self.screen)
			if self.turn:
				self.overAction = True
				if self.clicked():
					self.Send({"action":"talk","player action":"choose secondary race","chosen race":self.secondary_races[self.secondary_race_rect_array.overWhichRect(x,y)],"playerid":self.num,"gameid":self.gameid})
					self.justclicked = 10
					self.wait()
					self.endTurn()

	def playCard(self,x,y):
		if self.turn:
			self.skip_button.draw(self.screen)
			if self.skip_button.onButton(x,y):
				self.skip_button.highlight(self.screen)
				self.overAction = True
				if self.clicked():
					self.justclicked = 10
					self.action = "choose move"
			elif self.players[self.num].hand:
				if self.players[self.num].hand_rect_array.overRectArray(x,y):
					self.overAction = True
					if self.clicked():
						card = self.players[self.num].hand[self.players[self.num].hand_rect_array.overWhichRect(x,y)]
						self.Send({"action":"talk","player action":"play card","card":card,"playerid":self.num,"gameid":self.gameid})
						self.justclicked = 10
						self.wait()
						self.resolveCard(card)

	def chooseOpponentCard(self,x,y):
		for i in range(self.number_players):
			if self.players[i].hand_rect_array.overRectArray(x,y):
				self.overAction = True
				if self.clicked():
					card = self.players[i].hand[self.players[i].hand_rect_array.overWhichRect(x,y)]
					self.Send({"action":"talk","player action":"remove card","card":card,"playerid":i,"gameid":self.gameid})
					self.justclicked = 10
					self.action = "choose move"
					self.wait()

	def takeCard(self,x,y):
		self.top_deck_array.draw(self.makeList(self.card_images,self.top_cards),self.screen)
		if self.turn and self.top_deck_array.overRectArray(x,y):
			self.overAction = True
			self.top_deck_array.enlarge(self.card_images[self.top_cards[self.top_deck_array.overWhichRect(x,y)]],self.screen)
			if self.clicked():
				self.Send({"action":"talk","player action":"take card","card":self.top_cards[self.top_deck_array.overWhichRect(x,y)],"playerid":self.num,"gameid":self.gameid})
				self.justclicked = 10
				self.wait()

				if self.players[self.num].bonus_take_card and not self.players[self.num].bonus_take_card_done:
					self.action = "take card"
					self.players[self.num].bonus_take_card_done = True
				else:
					self.action = "play card"
					self.endTurn()

	def placeHexagon(self,x,y):
		if self.turn and (self.hexgrid.thistype(x,y) == self.place_type or self.place_type == "all") and (self.hexgrid.close_neighbour(self.num,x,y) <= self.place_range or self.stage == "pick starting territory") and not self.hexgrid.occupied(x,y) and self.hexgrid.onboard(x,y) and (self.playing_card or not self.players[self.num].prevent_place_hex):
			self.overAction = True
			if self.clicked():
				self.Send({"action":"talk","player action":"place hexagon","hex position":[x,y],"playerid":self.num,"gameid":self.gameid})
				self.justclicked = 10
				self.wait()
				if self.playing_card:
					if self.place_extra_hex:
						self.place_extra_hex = False
					elif self.players[self.num].bonus_play_card and not self.players[self.num].bonus_play_card_done:
						self.players[self.num].bonus_play_card_done = True
						self.action = "play card"
					else:
						self.playing_card = False
						self.action = "choose move"
						self.place_type = "all"
						self.place_range = self.players[self.num].place_range

				elif self.players[self.num].bonus_place_hex and not self.players[self.num].bonus_place_hex_done and not self.stage == "pick starting territory":
					self.players[self.num].bonus_place_hex_done = True
					self.action = "place hexagon"
					self.place_type = "normal"
				else:
					self.action = "play card"
					self.endTurn()

	def removeHexagon(self,x,y):
		if self.turn and self.hexgrid.occupied(x,y) and self.hexgrid.onboard(x,y) and self.hexgrid.close_neighbour(self.num,x,y) <= 1:
			if  self.hexgrid.num_terr(x,y) <= self.attack_value - self.players[self.hexgrid.occupied_by(x,y)].defence_value:
				self.overAction = True
				if self.clicked():
					self.Send({"action":"talk","player action":"remove hexagon","hex position":[x,y],"playerid":self.num,"gameid":self.gameid})
					self.justclicked = 10
					self.wait()
					self.action = "choose move"
					if self.playing_card:
						if self.players[self.num].bonus_play_card and not self.players[self.num].bonus_play_card_done:
							self.players[self.num].bonus_play_card_done = True
							self.action = "play card"
						else:
							self.playing_card = False
							self.action = "choose move"

	def blockHexagon(self,x,y):
		if self.turn and not self.hexgrid.occupied(x,y) and self.hexgrid.onboard(x,y):
			self.overAction = True
			if self.clicked():
				self.Send({"action":"talk","player action":"block hexagon","hex position":[x,y],"playerid":self.num,"gameid":self.gameid})
				self.justclicked = 10
				self.wait()
				self.played_block_hex = True
				self.played_block_hex_pos.append([x,y])
				if self.playing_card:
					if self.players[self.num].bonus_play_card and not self.players[self.num].bonus_play_card_done:
						self.players[self.num].bonus_play_card_done = True
						self.action = "play card"
					else:
						self.playing_card = False
						self.action = "choose move"
				else:
					self.action = "play card"
					self.endTurn()

	def chooseMove(self,x,y):

		if self.turn and not self.hexgrid.occupied(x,y) and self.hexgrid.onboard(x,y) and self.hexgrid.close_neighbour(self.num,x,y) <= self.players[self.num].place_range:
			self.overAction = True
			if self.clicked():
				self.Send({"action":"talk","player action":"place hexagon","hex position":[x,y],"playerid":self.num,"gameid":self.gameid})
				self.justclicked = 10
				self.wait()
				if self.players[self.num].bonus_place_hex and not self.players[self.num].bonus_place_hex_done:
					self.action = "place hexagon"
					self.players[self.num].bonus_place_hex_done = True
				else:
					self.action = "play card"
					self.endTurn()
					

		elif self.turn and self.take_deck_pos.withinRect(x,y):
			self.overAction = True
			if self.clicked():
				self.Send({"action":"talk","player action":"choose take cards","card pickup number":self.players[self.num].pickup_number,"playerid":self.num,"gameid":self.gameid})
				self.justclicked = 10
				self.action = "take card"
				self.wait()
		

	def endTurn(self):
		self.players[self.num].bonus_place_hex_done = False
		self.place_extra_hex = False
		self.players[self.num].bonus_take_card_done = False
		self.players[self.num].bonus_play_card_done = False
		self.place_type = "all"


		print "sending"

		self.Send({"action":"endturn","playerid":self.num,"gameid":self.gameid})
		self.wait()

	def startTurn(self):
		if self.played_block_hex:
			self.played_block_hex = False
			self.hexgrid.unblockhex(self.played_block_hex_pos)
			self.wait()


	def clicked(self):
		if pygame.mouse.get_pressed()[0] and self.justclicked <= 0:
			return True
		else:
			return False

	def wait(self):
		print "waiting"
		self.running = False
		while not self.running:
			connection.Pump()
			self.Pump()
			self.screen.fill([255,255,255])
			self.drawAll()
			pygame.display.flip()

	def drawAll(self):
		self.screen.fill([255,255,255])
		self.drawBoard()
		self.drawDecks()
		self.drawPlayerCards()
		self.drawHUD()

	def setCursor(self):
		if self.overAction:
			pygame.mouse.set_cursor(*pygame.cursors.diamond)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
		self.overAction = False

	def Network_setgame(self,data):
		number_players = input("How many players?:")
		self.Send({"action":"setgame","number players":number_players})
		print "searching for other players..."
		
	def Network_startgame(self,data):
		self.running = True
		self.num = data["player"]
		self.gameid = data["gameid"]
		self.primary_races = data["primary races"]

		self.secondary_races = data["secondary races"]
		self.secondary_race_rect_array = RectArray(100,250,300,200,210,0,len(self.secondary_races))

		self.number_players = data["number players"]
		self.primary_race_rect_array = RectArray(100,250,300,200,210,0,len(self.primary_races))

		self.action = "choose primary race"

	def Network_endturn(self,data):
		self.running = True
		self.place_type = data["place type"]
		self.top_cards = []
		self.round_number = data["round number"]
		self.stage = data["stage"]

		if not data["player action"] == "same":
			self.action = data["player action"]

		self.place_type = data["place type"]

		if self.num == data["player"]:
			self.turn = True
			self.startTurn()
		else:
			self.turn = False
		
	def Network_playcard(self,data):
		self.running = True
		self.players[data["player"]].removefromhand(data["card"])

	def Network_chooseprimaryrace(self,data):
		self.running = True
		self.players[data["player"]].setPrimaryRace(data["primary race"])
		self.primary_races.remove(data["primary race"])
		self.primary_race_rect_array = RectArray(100,250,300,200,210,0,len(self.primary_races))

	def Network_choosesecondaryrace(self,data):
		self.running = True
		self.players[data["player"]].setSecondaryRace(data["secondary race"])
		self.secondary_races.remove(data["secondary race"])
		self.secondary_race_rect_array = RectArray(100,250,300,200,210,0,len(self.secondary_races))

	def Network_placehex(self,data):
		self.running = True
		self.hexgrid.change_owner(data["player"],data["x"],data["y"])

	def Network_removehex(self,data):
		self.running = True
		self.hexgrid.change_owner(-1,data["x"],data["y"])

	def Network_blockhex(self,data):
		self.running = True

	def Network_takecard(self,data):
		self.running = True
		self.players[data["player"]].addToHand(data["card"])
		self.top_cards.remove(data["card"])
		self.top_deck_array = RectArray(300,250,300,200,210,0,len(self.top_cards))
		
	def Network_removecard(self,data):
		self.running = True
		self.players[data["player"]].removefromhand(data["card"])

	def Network_choosetakecards(self,data):
		self.running = True
		self.top_cards = data["cards"]
		self.top_deck_array = RectArray(300,250,300,200,210,0,len(self.top_cards))

	def update(self):

		self.setCursor()
		self.x,self.y = pygame.mouse.get_pos()

		self.justclicked -= 1

		connection.Pump()
		self.Pump()

		self.clock.tick(60)

		self.drawAll()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()

		self.resolveAction(self.x,self.y)

		pygame.display.flip()


	def text_objects(self, text, font):
		#use for creating textboxes
		textSurface = font.render(text, True, [0,0,0])
		return textSurface, textSurface.get_rect()
		
class Player(object):

	def __init__(self,x,y):

		self.hand = []
		self.hand_rect_array = RectArray(0,0,0,0,0,0,0)

		self.deckxpos = x
		self.deckypos = y
		
		self.prevent_place_hex = False

		self.bonus_play_card = False
		self.bonus_play_card_done = False

		self.bonus_place_hex = False
		self.bonus_place_hex_done = False

		self.bonus_take_card = False
		self.bonus_take_card_done = False
		self.defence_value = 0	
		self.points = 0

		self.pickup_number =  3

		self.capture_ability = False
		
		self.place_range = 1
		
	def addToHand(self,card):
		self.hand.append(card)
		self.hand_rect_array = RectArray(self.deckxpos,self.deckypos,200,150,0,40,len(self.hand))
		
	def removefromhand(self,card):
		self.hand.remove(card)
		self.hand_rect_array = RectArray(self.deckxpos,self.deckypos,200,150,0,40,len(self.hand))

	def setPrimaryRace(self,prime_race):
		
		if prime_race == 0:
			self.defence_value += 1
		elif prime_race == 1:
			self.capture_ability = True
		elif prime_race == 2:
			self.bonus_play_card = True
		elif prime_race == 3:
			self.point_bonus = True
		elif prime_race == 4:
			self.place_range = 2
		elif prime_race == 5:
			self.bonus_place_hex = True
			
		
	def setSecondaryRace(self,sec_race):

		if sec_race == 0:
			self.points += 5
		elif sec_race == 1:
			self.bonus_take_card = True
		elif sec_race == 2:
			self.bonus_start_territory = True
		elif sec_race == 3:
			self.pickup_number = 5
		elif sec_race == 4:
			self.bonus_block_hex = True
		elif sec_race == 5:
			self.bonus_move_hex = True

class Button(object):
	def __init__(self,text,game):
		self.largeText = pygame.font.Font('freesansbold.ttf',40)
		self.TextSurf, self.TextRect = game.text_objects(text, self.largeText)
		self.TextRect.center = (game.resl.current_w/2,game.resl.current_h/2)

	def draw(self,screen):
		pygame.draw.rect(screen,[255,255,255],self.TextRect)
		screen.blit(self.TextSurf,self.TextRect)

	def highlight(self,screen):
		pygame.draw.rect(screen,[0,200,0],self.TextRect)							
		screen.blit(self.TextSurf, self.TextRect)

	def onButton(self,x,y):
		if self.TextRect[0] < x < self.TextRect[0]+ self.TextRect[2] and self.TextRect[1] < y < self.TextRect[1]+ self.TextRect[3]:
			return True
		else:
			return False

class Rect(object):

	def __init__(self,x,y,h,w):
		self.x = x
		self.y = y
		self.h = h
		self.w = w
		
	def withinRect(self,xpos,ypos):
		if self.x < xpos < self.x + self.w and self.y < ypos < self.y + self.h:
			return True
		else:
			return False
					
class RectArray(object):

	def __init__(self,x,y,h,w,x_trans,y_trans,number_rectangles):
		self.rectangles = []
		self.enlarge_rect = Rect(400,200,500,350)
		for i in range(number_rectangles):
			self.rectangles.append(Rect(x+i*x_trans,y+i*y_trans,h,w))

	def draw(self,images,screen):
		for j in range(len(self.rectangles)):
			screen.blit(pygame.transform.scale(images[j],[self.rectangles[j].w,self.rectangles[j].h]),[self.rectangles[j].x,self.rectangles[j].y])

	def enlarge(self,image,screen):
		screen.blit(pygame.transform.scale(image, [self.enlarge_rect.w,self.enlarge_rect.h]),[self.enlarge_rect.x,self.enlarge_rect.y])
			
	def overRectArray(self,x,y):
		over_rect = False
		for rect in self.rectangles:
			if rect.withinRect(x,y):
				over_rect = True
		return over_rect

	def overWhichRect(self,x,y):
		which_rect = -1
		for i in range(len(self.rectangles)):
			if self.rectangles[i].withinRect(x,y):
				which_rect = i
		return which_rect

g = BoardGame()
while 1:
	g.update()
				
				
		
