import locale
from locale_data import Locale_data

class Localization:
	def __init__(self, language):
		if language in Locale_data:
			self.language = language
		else:
			self.language = "en_US"

	def get(self, text):
		return Locale_data[self.language][text]