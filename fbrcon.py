from twisted.internet.protocol import Protocol, Factory

from fbrconpacket import FBRconPacket

class FBRconFactory(Factory):
	isServer = False
	
	def __init__(self, isServer = False, params = {}):
		self.isServer = isServer
		self.params   = params

class FBRconProtocol(Protocol):
	__seq = 0
	__buffer = ""

	def __init__(self):
		pass
		
	def connectionMade(self):
		self.__seq = 0
		self.__buffer = ""
	
	def sendRequest(self, strings):
		"""sends something to the other end, returns a Deferred"""
		raise NotImplementedError("sendRequest needs to be implemented in a subclass")
	
	def gotResponse(self, packet):
		"""handles incoming response packets"""
		raise NotImplementedError("gotResponse needs to be implemented in a subclass")
	
	def sendResponse(self, seq):
		"""called by gotRequest to send a response"""
		raise NotImplementedError("sendResponse needs to be implemented in a subclass")
	
	def gotRequest(self, packet):
		"""handles incoming request packets"""
		raise NotImplementedError("gotRequest needs to be implemented in a subclass")
		
	def dataReceived(self, data):
		""" recieves data off the wire """
		self.__buffer = self.__buffer + data
		pkt = FBRconPacket()
		while pkt.deserialize(self.__buffer): # if successful, we deser'd a full packet.
			if pkt.isResponse: 
				self.gotResponse(pkt)
			else:
				self.gotRequest(pkt)
			self.__buffer = self.__buffer[pkt.len:]
			pkt = FBRconPacket()

	### helper functions to abstract away FBRconPacket
	def getSeq(self):
		seq = self.__seq
		self.__seq = (self.__seq + 1) & 0x3fffffff
		return seq
	
	def peekSeq(self):
		return self.__seq
	
	def EncodeClientRequest(self, words):
		return FBRconPacket(False, False, self.getSeq(), words).serialize()

	def EncodeClientResponse(self, sequence, words):
		return FBRconPacket(False, True, sequence, words).serialize()
	
	def EncodeServerRequest(self, words):
		return FBRconPacket(True, False, self.getSeq(), words).serialize()
	
	def EncodeServerResponse(self, sequence, words):
		return FBRconPacket(True, True, sequence, words).serialize()
