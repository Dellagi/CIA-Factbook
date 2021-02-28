# --> coding: utf-8 -*-

import json, pyfiglet, os
from PyInquirer import style_from_dict, Token, prompt, Separator
from PyInquirer import Validator, ValidationError
from dbhandler import db_handler
from validators import *
from datetime import datetime
import hashlib, sys, re, math
from prettytable import PrettyTable
import numpy as np
import matplotlib.pyplot as plt


from Datascientist_Class import Data_class



class Consultant_class(Data_class):
	def __init__(self):
		super().__init__()


	def signin(self):
		try:
			questions = [{"name": "username", "type": "input", "message": "Your chosen username :", "validate": "AsciiValidator"},\
			 {"name": "password", "type": "password", "message": "Your chosen password :", "validate": "AsciiValidator"}]
			answers = prompt(questions, style=self.style)
			tmp_obj = db_handler("users")
			hashed_pass = hashlib.md5(answers['password'].encode('utf-8')).hexdigest()
			resp_ = tmp_obj.sql_run("SELECT password, privilege FROM users WHERE username=='%s'"%answers['username'])
			if len(resp_):
				if hashed_pass == resp_[0][0]:
					return ('signin', resp_[0][1])
			return ('signin', -1)
		except:
			return ('signin', 500)



if __name__ == "__main__":
	while True:
		try:
			obj_ = Consultant_class()
			obj_.generate_menu(3, 1)
		except:
			obj_.generate_menu(3, 1)
