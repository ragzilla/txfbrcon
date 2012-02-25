from twisted.internet import defer
from twisted.application.service import MultiService
from twisted.application.internet import TCPClient

from clientrcon import getClientRconFactory

class RconManager(MultiService):
	""" runs multiple rcon instances """
	mongo   = None
	servers = {}
	subs    = {}
	
	def __init__(self):
		MultiService.__init__(self)
	
	@defer.inlineCallbacks
	def startService(self):
		print "RconManager.startService..."
		self.mongo   = self.getRootService().getMongo()
		servers = yield self.mongo.servers.find()
		for server in servers:
			print "Starting server:",server
			factory = getClientRconFactory(server, self)
			client  = TCPClient(server["ip"], int(server["port"]), factory)
			client.setServiceParent(self)
			server["factory"] = factory
			self.servers[server["tag"]] = server
		print self.servers
		MultiService.startService(self)
		
	def getInstance(self, tag):
		if tag in self.servers:
			return self.servers[tag]["factory"].instance
		return None

	def sendRcon(self, tag, strings):
		if tag in self.servers:
			return self.servers[tag]["factory"].instance.sendRequest(strings)
		return None

	def getRootService(self):
		return self.parent.getRootService()
	
	def postMessage(self, facility, params):
		print "postMessage(%s): %s" % (facility,params,)
		if facility in self.subs:
			for callback in self.subs[facility]:
				callback(params)
	
	def subMessage(self, facility, callback):
		if facility in self.subs:
			self.subs[facility].append(callback)
		else:
			self.subs[facility] = [callback,]

