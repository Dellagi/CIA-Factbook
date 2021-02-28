from PyInquirer import Validator, ValidationError
import re



class PhoneNumberValidator(Validator):
	def validate(self, document):
		ok = re.match('^([01]{1})?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\s?((?:#|ext\.?\s?|x\.?\s?){1}(?:\d+)?)?$', document.text)
		if not ok:
			raise ValidationError(
				message='Please enter a valid phone number',
				cursor_position=len(document.text))


class NumberValidator(Validator):
	def validate(self, document):
		ok = None
		try:
			float(document.text)
			ok = 1
		except:
			pass
		if not ok:
			raise ValidationError(
				message='Please enter a valid number',
				cursor_position=len(document.text))


class PercentValidator(Validator):
	def validate(self, document):
		ok = None
		try:
			if '%' in document.text:
				float(document.text.replace('%', ''))
				ok = 1
		except:
			pass
		if not ok:
			raise ValidationError(
				message='Please enter a valid percent (Ex: 12.5 or 12.5%)',
				cursor_position=len(document.text))



class YearValidator(Validator):
	def validate(self, document):
		ok = None
		try:
			if len(document.text)==4:
				int(document.text)
				ok = 1
			elif not len(document.text):
				ok = 1
		except:
			pass
		if not ok:
			raise ValidationError(
				message='Please enter a valid year (Ex: 2017)',
				cursor_position=len(document.text))


class DetteValidator(Validator):
	def validate(self, document):
		ok = None
		try:
			int(document.text.replace(',', '').replace('$', '').replace(' ',''))
			ok = 1
		except:
			pass
		if not ok:
			raise ValidationError(
				message='Please enter a valid amount (Ex: $450,000,000)',
				cursor_position=len(document.text))


class BirthValidator(Validator):
	def validate(self, document):
		ok = regex.match('^\d{1,2}\/\d{1,2}\/\d{4}$', document.text)
		if not ok:
			raise ValidationError(
				message='Please enter a valid date',
				cursor_position=len(document.text))



class AsciiValidator(Validator):
	def validate(self, document):
		if not len(document.text):
			raise ValidationError(
				message='field cannot be left null',
				cursor_position=len(document.text))
		try:
			document.text.encode('ascii')
		except:
			raise ValidationError(
				message='Non ASCII Chars are not allowed',
				cursor_position=len(document.text))

