
class Player:
	""" this represents a bf3 player """

	def __init__(self, name, guid):
		self.name  = name
		self.lname = name.lower()
		self.guid  = guid
		print "adding:",self.lname
	
	def finalize(self):
		pass
	
	def onAuthenticated(self):
		print "%s authenticated." % (self.lname)
