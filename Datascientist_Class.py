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

from MainClass import AdminClass


class Data_class(AdminClass):
	def __init__(self):
		super().__init__()

	def correction(self):
		try:
			auth_fields = ["superficie", "population", "croissance_demo", "inflation", "dette", "taux_chomage","taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]
			country_name_q = [{'message': 'Do you propose to modify:', "type": "list", "name": "chosen_field", "choices": auth_fields},
			 {'filter':lambda val: val.lower(),'message': "What's the name of the country?",'name': 'country_name','type': 'input','validate': AsciiValidator}]
			answersx = prompt(country_name_q, style=self.style)
			tmp_obj = db_handler("factbook")
			resp_ = tmp_obj.sql_run("SELECT * FROM factbook where lower(country_name)=='%s'"%answersx['country_name'])
			if len(resp_):
				temp_resp_ = ['[Current value: %s]'%str(i) for i in resp_[0][2:]]
				country_form = [{'message': 'superficie (in square kilometers): '+temp_resp_[0],'name': 'superficie','type': 'input','validate': NumberValidator,\
				"filter": lambda val: val+' sq km'},{'message': 'Population :'+temp_resp_[1],'name': 'population','type': 'input','validate': NumberValidator}
				,{'message': 'Demographic growth (format ex: 34.5%) :'+temp_resp_[2],'name': 'croissance_demo','type': 'input','validate': PercentValidator}
				,{'message': 'inflation (format ex: 2%) :'+temp_resp_[3],'name': 'inflation','type': 'input','validate': PercentValidator}
				,{'message': 'dette (format ex: 20%) :'+temp_resp_[4],'name': 'dette','type': 'input','validate': PercentValidator}
				,{'message': 'Unemployement rate (format ex: 20%) :'+temp_resp_[5],'name': 'taux_chomage','type': 'input','validate': PercentValidator}
				,{'message': 'Government expenditure on health (format ex: 20%) :'+temp_resp_[6],'name': 'taux_depense_sante','type': 'input'\
				,'validate': PercentValidator},{'message': 'government expenditure on education (format ex: 20%) :'+temp_resp_[7],\
				'name': 'taux_depense_educ','type': 'input','validate': PercentValidator},
				{'message': 'government expenditure on military (format ex: 20%) :'+temp_resp_[8],'name': 'taux_depense_militaire','type': 'input','validate': PercentValidator}
				,{'message': 'nullx','name': 'nullx','type': 'input','when': lambda answers: print('All good!, Please check later your application status.')}]
				country_form = country_form[auth_fields.index(answersx['chosen_field'])]				
				answers = prompt(country_form, style=self.style)
				insert_tmp = [str(i) for i in resp_[0][2:]]
				insert_tmp[auth_fields.index(answersx['chosen_field'])] = answers[answersx['chosen_field']]
				tmp_obj = db_handler("update_request")
				sql_input = "INSERT INTO update_request (country_name, superficie, population, croissance_demo, inflation, dette, taux_chomage,\
		 			taux_depense_sante, taux_depense_educ, taux_depense_militaire) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"\
					%(answersx["country_name"].capitalize(), insert_tmp[0], insert_tmp[1], insert_tmp[2], insert_tmp[3],\
						insert_tmp[4], insert_tmp[5], insert_tmp[6], insert_tmp[7], insert_tmp[8])
				tmp_obj.sql_run(sql_input)
				return ('propose_modification', 1)
			else:
				return ('propose_modification', 0)
		except :
			return ('propose_modification', 500)


if __name__ == "__main__":
	while True:
		try:
			obj_ = Data_class()
			obj_.generate_menu(1, 1)
		except:
			obj_.generate_menu(3, 1)

