from twisted.internet import defer
from player import Player

class Server:
	""" this represents a bf3 server """

	def __init__(self, rcon):
		self.teams = {}
		self.players = {}
		self.rcon = rcon
	
	def addPlayer(self, name, guid):
		lname = name.lower()
		if lname in self.players:
			return self.players[lname]
		ph = Player(name, guid)
		self.players[ph.lname] = ph
		return ph
	
	def delPlayer(self, name):
		lname = name.lower()
		if lname in self.players:
			ph = self.players[lname]
			ph.finalize()
			del self.players[lname]
			del ph
	
	@defer.inlineCallbacks
	def getPlayer(self, name):
		lname = name.lower()
		if lname in self.players:
			defer.returnValue(self.players[lname])
			return
		### player not found, so let's create him
		pl = yield self.rcon.admin_listOnePlayer(name)
		ph = self.addPlayer(pl['name'], pl['guid'])
		defer.returnValue(ph)
		return
	

