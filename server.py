import PodSixNet.Channel
import PodSixNet.Server
import random
from random import shuffle
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):
	
	def Network(self,data):
		print data

	def Network_talk(self,data):
		gameid = data["gameid"]
		self._server.passToGame(data,gameid)
			
	def Network_setgame(self,data):
		number_players = data["number players"]
		self._server.setGame(number_players)

	def Network_endturn(self,data):
		gameid = data["gameid"]
		self._server.endTurn(data,gameid)
		
class BoardServer(PodSixNet.Server.Server):
	def __init__(self, *args, **kwargs):
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		self.currentIndex = 0
		self.currentPlayers = 0

	channelClass = ClientChannel

	def Connected(self,channel,addr):
		print 'new connection:', channel
		
		if self.queue == None:
			self.unset = 1
			self.currentIndex+=1
			self.currentPlayers+=1
			channel.gameid = self.currentIndex
			channel.Send({"action":"setgame"})
			self.first_channel = channel
			while self.unset:
				self.Pump()
				sleep(0.01)
		else:
			channel.gameid = self.currentIndex
			self.queue.player_channel.append(channel)
			self.currentPlayers+=1
			
			if self.currentPlayers == self.queue.number_players:
				primary_races = random.sample(range(6), self.queue.number_players+1)
				print primary_races
				secondary_races = random.sample(range(6), self.queue.number_players+1)
				print secondary_races
			
				for i in range(self.queue.number_players):
					self.queue.player_channel[i].Send({"action":"startgame","number players":self.queue.number_players,"player":i,"gameid":self.queue.gameid,"primary races":primary_races,"secondary races":secondary_races})
					
				self.games.append(self.queue)
				self.queue = None
				self.currentPlayers = 0

	def passToGame(self,data,gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].unpackData(data)
					
	def setGame(self,number_players):
		self.queue = Game(self.first_channel, self.currentIndex, number_players)
		self.unset = 0

	def endTurn(self,data,gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].endTurn(data)
		
class Game:
	def __init__(self, player0, currentIndex, number_players):
	
		self.number_players = number_players
		self.player_channel = []
		self.player_channel.append(player0)

		self.gameid = currentIndex
				
		self.take_deck = Deck(10)
		self.discards = Deck(0)
		self.top_cards = []
		
		self.turn = 0
		self.round_number = 0

		self.stage = "pick primary race"

		self.bonus_starting_territory = False
		self.number_territories_picked = 0

		self.end_turn_switcher = {
				"pick primary race":self.pickPrimaryRace,
				"pick secondary race":self.pickSecondaryRace,
				"pick starting territories":self.pickStartingTerritories,
				"main":self.main
				}

	def pickPrimaryRace(self,data):
		self.turn += 1
		if self.turn%self.number_players == 0:
			self.turn = self.number_players - 1
			self.stage = "pick secondary race"
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick secondary race","place type":"all","round number":self.round_number,"player action":"choose secondary race","player":self.turn%self.number_players})
		else:
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick primary race","place type":"all","player":self.turn%self.number_players,"player action":"same","round number":self.round_number})

	def pickSecondaryRace(self,data):
		self.turn -= 1
		if self.turn == -1:
			self.turn = 0
			self.stage = "pick starting territories"
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick starting territory","place type":"terr","round number":self.round_number,"player action":"place hexagon","player":self.turn%self.number_players})
		else:
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick secondary race","place type":"all","player":self.turn%self.number_players,"player action":"same","round number":self.round_number})

	def pickStartingTerritories(self,data):
		self.turn += 1
		print self.turn
		if self.turn%self.number_players == 0 and self.number_territories_picked == 1 and not self.bonus_starting_territory:
			self.turn = 0
			self.stage = "main"
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"main game","place type":"all","player":self.turn%self.number_players,"player action":"play card","round number":self.round_number})
		elif self.turn%self.number_players == 0 and self.number_territories_picked == 1 and self.bonus_starting_territory:
			self.turn = self.bonus_starting_territory_player
			self.bonus_starting_territory = False
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick starting territory","place type":"terr","player":self.turn%self.number_players,"player action":"place hexagon","round number":self.round_number})
			self.turn = -1

		elif self.turn%self.number_players == 0:
			self.number_territories_picked += 1
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick starting territory","place type":"terr","player":self.turn%self.number_players,"player action":"place hexagon","round number":self.round_number})

		else:
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"pick starting territory","place type":"terr","player":self.turn%self.number_players,"player action":"place hexagon","round number":self.round_number})

	def main(self,data):
		self.turn += 1
		if self.turn%self.number_players == 0:
			self.round_number += 1
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"main game","place type":"all","player":self.turn%self.number_players,"player action":"same","round number":self.round_number})
		else:
			for player in self.player_channel:
				player.Send({"action":"endturn","stage":"main game","place type":"all","player":self.turn%self.number_players,"player action":"same","round number":self.round_number})


	def endTurn(self,data):


		if not self.top_cards:
			pass
		else:
			self.discards.combineDecks(self.top_cards)
			self.top_cards = []

		return self.end_turn_switcher[self.stage](data)


	def unpackData(self,data):
		switcher = {
				"choose primary race":self.choosePrimaryRace,
				"choose secondary race":self.chooseSecondaryRace,
				"play card":self.playCard,
				"take card":self.takeCard,
				"place hexagon":self.placeHexagon,
				"remove hexagon":self.removeHexagon,
				"block hexagon":self.blockHexagon,
				"choose take cards":self.chooseTakeCards,
				"remove card":self.removeCard

				}

		return switcher[data["player action"]](data)

	def choosePrimaryRace(self,data):
		for player in self.player_channel:
			player.Send({"action":"chooseprimaryrace","primary race":data["chosen race"],"player":data["playerid"]})

	def chooseSecondaryRace(self,data):
		if data["chosen race"] == 2:
			self.bonus_starting_territory = True
			self.bonus_starting_territory_player = data["playerid"]

		for player in self.player_channel:
			player.Send({"action":"choosesecondaryrace","secondary race":data["chosen race"],"player":data["playerid"]})

	def playCard(self,data):
		if not data["card"] == -1:
			self.discards.deck.append(data["card"])
			for player in self.player_channel:
				player.Send({"action":"playcard","card":data["card"],"player":data["playerid"]})

	def chooseTakeCards(self,data):
		if len(self.take_deck.deck) < data["card pickup number"]:
			self.take_deck.combineDecks(self.discards.deck)
			self.discards.emptyDeck()
		self.top_cards = self.take_deck.deck[0:data["card pickup number"]]
		self.take_deck.deck[0:data["card pickup number"]] = []
		for player in self.player_channel:
			player.Send({"action":"choosetakecards","cards":self.top_cards})

	def takeCard(self,data):
		self.top_cards.remove(data["card"])
		for player in self.player_channel:
			player.Send({"action":"takecard","card":data["card"],"player":data["playerid"]})

	def removeCard(self,data):
		self.discards.deck.append(data["card"])
		for player in self.player_channel:
			player.Send({"action":"removecard","card":data["card"],"player":data["playerid"]})

	def placeHexagon(self,data):
		for player in self.player_channel:
			player.Send({"action":"placehex","x":data["hex position"][0],"y":data["hex position"][1],"player":data["playerid"]})

	def removeHexagon(self,data):
		for player in self.player_channel:
			player.Send({"action":"removehex","x":data["hex position"][0],"y":data["hex position"][1]})

	def blockHexagon(self,data):
		for player in self.player_channel:
			player.Send({"action":"blockhex","x":data["hex position"][0],"y":data["hex position"][1]})
					
class Deck(object):

	def __init__(self,number_cards):
		self.deck = [i for i in range(number_cards) for _ in range(3)]
		self.shuffleDeck()
		
	def shuffleDeck(self):
		shuffle(self.deck)
		
	def combineDecks(self,decktomerge):
		self.deck = self.deck + decktomerge
		
	def emptyDeck(self):
		self.deck = []
		
		
print "STARTING SERVER ON LOCALHOST"
address = raw_input("Host:Port (localhost:8000): ")
if not address:
	host, port = "localhost", 8000
else:
	host,port = address.split(":")	
bgServe = BoardServer(localaddr=(host,int(port)))
while True:
	bgServe.Pump()
	sleep(0.01)
