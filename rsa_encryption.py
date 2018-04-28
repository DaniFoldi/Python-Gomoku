class RSA_encryption:
	def __init__(self):
		try:
			from Crypto.PublicKey import RSA
		except ImportError:
			import pip
			pip.main(["install", "PyCrypto"])
			from Crypto.PublicKey import RSA
		self.key = RSA.generate(2048)
		self._private_key = self.key.exportKey('DER')
		self.public_key = self.key.publickey().exportKey('DER')

	def get_public_key(self):
		return self.public_key

	def decrypt_message(self, data, public_key):
		from Crypto.PublicKey import RSA
		public_key_decryptor = RSA.importKey(public_key)
		return public_key_decryptor.decrypt(data)

	def encrypt_message(self, data):
		from Crypto.PublicKey import RSA
		private_key_encryptor = RSA.importKey(self._private_key)
		return private_key_encryptor.encrypt(data, 'x')[0]