from struct import *

class FBRconPacket:
	isFromServer = None
	isResponse   = None
	sequence     = None
	words        = []
	len          = 0
	
	def __init__(self, isFromServer=None, isResponse=None, sequence=0, words=[]):
		self.isFromServer = isFromServer
		self.isResponse   = isResponse
		self.sequence     = sequence
		self.words        = words
		if self.isFromServer != None:
			foo = self.serialize()
		else:
			self.len          = 0
	
	def serialize(self):
		"""returns a serialized version of the packet, suitable for putting on the wire"""
		[encoded, self.len] = self.EncodePacket(self.isFromServer, self.isResponse, self.sequence, self.words)
		return encoded
	
	def deserialize(self, data):
		"""deserializes from text data, suitable for reading from the wire
		   returns True if we successfully deser'd a packet
		"""
		buflen = len(data)
		if buflen < 12: return False         ### full header present?
		pktlen = self.DecodeInt32(data[4:8]) ### pull out the len
		if buflen < pktlen: return False     ### do we have the full packet buffered?
		self.len = pktlen
		[self.isFromServer, self.isResponse, self.sequence, self.words] = self.DecodePacket(data)
		return True
	
	def EncodePacket(self, isFromServer, isResponse, sequence, words):
		encodedHeader = self.EncodeHeader(isFromServer, isResponse, sequence)
		encodedNumWords = self.EncodeInt32(len(words))
		[wordsSize, encodedWords] = self.EncodeWords(words)
		encodedSize = self.EncodeInt32(wordsSize + 12)
		return [encodedHeader + encodedSize + encodedNumWords + encodedWords, wordsSize + 12]

	def DecodePacket(self, data):
		[isFromServer, isResponse, sequence] = self.DecodeHeader(data)
		wordsSize = self.DecodeInt32(data[4:8]) - 12
		words = self.DecodeWords(wordsSize, data[12:])
		return [isFromServer, isResponse, sequence, words]	

	def EncodeHeader(self, isFromServer, isResponse, sequence):
		header = sequence & 0x3fffffff
		if isFromServer:
			header += 0x80000000
		if isResponse:
			header += 0x40000000
		return pack('<I', header)

	def DecodeHeader(self, data):
		[header] = unpack('<I', data[0 : 4])
		return [header & 0x80000000, header & 0x40000000, header & 0x3fffffff]

	def EncodeInt32(self, size):
		return pack('<I', size)

	def DecodeInt32(self, data):
		return unpack('<I', data[0 : 4])[0]

	def EncodeWords(self, words):
		size = 0
		encodedWords = ''
		for word in words:
			strWord = str(word)
			encodedWords += self.EncodeInt32(len(strWord))
			encodedWords += strWord
			encodedWords += '\x00'
			size += len(strWord) + 5
		return size, encodedWords

	def DecodeWords(self, size, data):
		numWords = self.DecodeInt32(data[0:])
		words = []
		offset = 0
		while offset < size:
			wordLen = self.DecodeInt32(data[offset : offset + 4])
			word = data[offset + 4 : offset + 4 + wordLen]
			words.append(word)
			offset += wordLen + 5
		return words

	def __str__(self):
		return "IsFrom%s, %s, Sequence: %u, Words: \"%s\"" % (
			self.isFromServer and "Server" or "Client",
			self.isResponse and "Response" or "Request",
			self.sequence,
			"\" \"".join(self.words),
			)