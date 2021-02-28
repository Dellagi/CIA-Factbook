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


header_banner = pyfiglet.figlet_format("CIA Factbook")



class AdminClass:
	def __init__(self):
		self.privilege = {0:"admin", 1:"data_scientist", 2:"geographe", 3: "consultant"}
		self.reversed_privilege = {value : key for (key, value) in self.privilege.items()}
		self.menu_ref = {'-> create an account':[[0], 'signup'], '-> login':[[3], 'signin'],\
		'-> display a country':[[0,1,2,3], 'display_country'], '-> propose a correction' : [[1,3], 'correction'],\
		'-> review corrections':[[0,2], 'review'], '-> add/modify a country' : [[0,2], 'modify_country'],\
		'-> remove a country' : [[0], 'remove_country'], '-> display histogramme' : [[0,1], 'plot_hist'],\
		'-> display boxplot' : [[0,1], 'plot_boxplot'], '-> remove an account' : [[0], 'remove_account'], "-> logout":[[0,1,2], 'logout'], "-> exit":[[0,1,2,3], 'sys_exit']}
		self.field_names = ["country_name", "superficie", "population", "croissance_demo", "inflation", "dette", "taux_chomage",\
		 "taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]
		self.style = style_from_dict({
			Token.QuestionMark: '#E91E63 bold',
			Token.Selected: '#673AB7 bold',
			Token.Instruction: '',	# default
			Token.Answer: '#2196f3 bold',
			Token.Question: '',
		})
		tmp_obj = db_handler("factbook")
		resp_ = tmp_obj.sql_run("SELECT * FROM factbook;")
		if not len(resp_):
			from load_factbook import factbook_processor
			obj_ = factbook_processor()
			obj_.insert_db()


	def generate_menu(self, privilege_id, show_headers=0):
		while 1:
			if show_headers:
				os.system('clear')
				print(header_banner)
			questions, resp_ = None, None
			base_format_menu = [{"type": "list", "name": "Main_option", "choices": [], "filter": lambda val: val.lower()}]
			base_format_menu[0]["message"] = "######## %s menu ########"%self.privilege[privilege_id]
			for feature_ in self.menu_ref.keys():
				if privilege_id in self.menu_ref[feature_][0]:
					base_format_menu[0]["choices"].append(feature_)
			answers = prompt(base_format_menu, style=self.style)
			resp_ = eval('self.' + self.menu_ref[answers['Main_option']][-1] + '()')
			if resp_[-1] == 500:
				print("[-] Internal Error occured, Error: " + resp_[0])
			elif resp_[0] == 'signin':
				os.system('clear')
				print(header_banner)
				if resp_[1] == -1:
					print("[-] Incorrect Login User/Pass combination")
					self.generate_menu(3)
				else:
					self.generate_menu(int(resp_[1]), 1)
			elif resp_[0] in ['propose_modification', 'modify_country']:
				if resp_[1] == 1:
					print("[!] Operation was successful")
				else:
					print("[-] 404 was not found")
			elif resp_[0] == 'signup':
				if resp_[1] == 1:
					print("[!] Operation was successful")
				else:
					print("[-] Account already exists")
			elif resp_[0] == 'remove_account':
				if resp_[1] == 1:
					print("[!] Operation was successful")
				else:
					print("[-] No accounts were found")
			input("Press [Enter] to continue...")


	def signup(self):
		try:
			signup_form = [{"name": "privilege", "type": "list", "filter": lambda val: val.lower().replace(' ', '_'),\
			 "choices": ["Data scientist", "Geographe"], "message": "What type of membership do you want?"},
			  {"name": "phone_number", "type": "input", "message": "What's your phone number?", "validate": PhoneNumberValidator},
			   {"name": "username", "type": "input", "message": "Your chosen username :", "validate": AsciiValidator},
				{"name": "password", "type": "password", "message": "Your chosen password :", "validate": AsciiValidator},
				 {"name": "firstname", "type": "input", "message": "Your firstname :", "validate": AsciiValidator},
				  {"name": "lastname", "type": "input", "message": "Your lastname :", "validate": AsciiValidator},
				   {"name": "birthday", "type": "input", "message": "You birthday ? (mm/jj/YYYY) :", "validate": BirthValidator},
					{"name": "nullx", "type": "input", "message": "nullx", "when": lambda answers: print('The informations will be communicated to the Database.')}]
			answers = prompt(signup_form, style=self.style)
			tmp_obj = db_handler("users")
			resp_ = tmp_obj.sql_run("SELECT ID FROM users WHERE username=='%s'"%answers['username'])
			if not len(resp_):
				tmp_obj = db_handler("users")
				answers['password'] = hashlib.md5(answers['password'].encode('utf-8')).hexdigest()
				x = tmp_obj.sql_run("INSERT INTO users (firstname, lastname, username, password, privilege, birthday, phone_number) values('%s', '%s', '%s', '%s', %d, '%s', '%s')"%(answers['firstname'], answers['lastname'], answers['username'], answers['password'], self.reversed_privilege[answers['privilege']], answers['birthday'], answers['phone_number']))
				return ('signup', 1)
			else:
				return ('signup', 0)
		except Exception as e:
			return ('signup: {}'.format(str(e)), 500)


	def search_country(self, criteria, threshold, operator_):
		tmp_obj, resu_ = db_handler("factbook"), []
		sql_x = "select country_name,%s from factbook where country_name IS NOT NULL and country_name!='none';"%criteria
		resp_ = tmp_obj.sql_run(sql_x)
		for country_ in resp_:
			years_ = re.findall('(\d{4})', str(country_[1]))
			years_ = list(set([int(icol) for icol in years_[:] if icol[:2] in ['19','20']]))
			years_ = [str(icol) for icol in years_[:]]
			for year_ in years_:
				info_ = country_[1]
				if str(info_).lower() != 'none':
					for year_info in info_.split("++"):
						if year_ in year_info:
							year_info = year_info.replace(",","")
							year_info_re = re.findall(r'[-+]?\d*\.\d+|\d+', year_info)
							if len(year_info_re):
								percent = ['%' if '%' in year_info else ''][0]
								value_ = year_info_re[0]
								if eval(value_+ operator_ +threshold):
									resu_.append([year_, country_[0], value_+percent])
								break
		return resu_


	def display_country(self):
		try:
			countries_lst = [{'message': 'Choose a country :',\
			 'type': 'list', 'name': 'chosen_country',\
			  'choices': []}, {'message': 'Do you want the age classes or other infos ?',\
			 'type': 'list', 'name': 'chosen_critiria',\
			  'choices': ['Age classes', 'Other infos']},
			  {'type': 'checkbox', 'message': 'Select countries', 'name': 'ageclasses_countries',
			'choices': [Separator('= The countries available =')], \
			'validate': lambda answer: True if len(answer)>0 and len(answer)<=10 else 'You must choose at least 1 country.'},
			{'type': 'confirm', 'message': 'Do you have a want to apply a filter to countries?', 'name': 'special_filters', 'default': False}]
			answers = prompt(countries_lst[-1], style=self.style)
			if answers['special_filters']:
				special_filters = [{'message': 'Choose a filter :',\
			 'type': 'list', 'name': 'chosen_filter',\
			  'choices': ["superficie", "population", "croissance_demo", "inflation", "dette", "taux_chomage",\
			 "taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]}, {'message': 'Which operator you want to apply ?',\
			 'type': 'list', 'name': 'chosen_filter_op',\
			  'choices': ['higher', 'lower', 'equal']}]
				answers = prompt(special_filters, style=self.style)
				answers2 = prompt({'type': 'input','name': 'threshold','message': 'You want the %s %s than/to:'\
					%(answers['chosen_filter'], answers['chosen_filter_op'])}, style=self.style)
				lst_country = self.search_country(answers['chosen_filter'], answers2['threshold'], ['>' if answers['chosen_filter_op']=='higher' else 
					['<' if answers['chosen_filter_op']=='lower' else '=='][0]][0])

			answers = prompt(countries_lst[1], style=self.style)
			tmp_obj = db_handler("factbook")
			resp_ = tmp_obj.sql_run("select country_name from factbook where country_name IS NOT NULL and country_name!='none' Order By country_name;")
			if 'lst_country' in locals():
				resp_ = [i for i in resp_[:] if i[0] in [j[1] for j in lst_country]]
			countries_lst[0]['choices'] = [i[0] for i in resp_]
			countries_lst[2]['choices'] += [{'name': i[0]} for i in resp_]
			if answers['chosen_critiria']=='Other infos':
				answers = prompt(countries_lst[0], style=self.style)
				resp_ = tmp_obj.sql_run("select * from factbook where country_name=='%s';"%answers['chosen_country'])
				len_r = len(''.join([str(i) for i in resp_[0][1:-1]]))
				tty_row, tty_col = os.popen('stty size', 'r').read().split()
				years_ = re.findall('(\d{4})', ' | '.join(str(icol) for icol in resp_[0]))
				years_ = sorted(list(set([int(icol) for icol in years_[:] if icol[:2] in ['19','20']])), reverse=True)
				years_ = [str(icol) for icol in years_[:]]
				t_rows = 1 if int(tty_col)/2-(len_r/(1+len(years_)))>45 else 2
				for l in range(t_rows):
					ptable = PrettyTable()
					ptable.title="Country : %s"%answers['chosen_country']
					field_names = [["Year", "superficie", "population", "croissance_demo", "inflation"]]
					if t_rows==2:
						field_names.append(["Year", "dette", "taux_chomage", "taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"])
					else:
						field_names[0] += ["dette", "taux_chomage", "taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]
					ptable.field_names = field_names[l]
					if not len(years_):
						years_ = ['0']
					for year_ in years_:
						tmp_row = [year_]
						tmp_resp = [list(resp_[0][2:-1])[:4], list(resp_[0][2:-1])[4:]]
						if t_rows==1:
							tmp_resp = [sum(tmp_resp, [])]
						for info_ in tmp_resp[l]:
							if str(info_).lower() != 'none' and year_ in info_:
								for year_info in info_.split("++"):
									if year_ in year_info:
										try:
											year_info = year_info.replace(year_info[year_info.index("("):year_info.index(")")+1], '')
										except:
											pass
										vx = year_info
										tmp_row.append([vx, vx[:15]+'...'][0 if len(vx)<=20 else 1])
							elif str(info_).lower() != 'none' and 'sq km' in info_:
								vx = info_
								tmp_row.append([vx, vx[:15]+'...'][0 if len(vx)<=20 else 1])
							elif str(info_).lower() != 'none':
								vx = info_
								tmp_row.append([vx, vx[:15]+'...'][0 if len(vx)<=20 else 1])
							else:
								tmp_row.append('N/a')
						ptable.add_row(tmp_row)
					print(ptable)
			else:
				answers = prompt(countries_lst[2], style=self.style)
				sql_q = "select * from factbook where country_name IN {};".format(tuple(answers['ageclasses_countries']))
				resp_ = tmp_obj.sql_run(sql_q)
				ptable = PrettyTable()
				ptable.title="Age classes"
				tmp_dict_ = ['Country', '0-14 years', '15-24 years', '25-54 years', '55-64 years', '65 years and over']
				ptable.field_names = tmp_dict_
				for v in resp_:
					tmp_row = [v[1]]
					for key_class in tmp_dict_[1:]:
						s = eval(v[-1])[key_class]['text']
						tmp_row.append(s[:s.index(" ")+1])
					ptable.add_row(tmp_row)
				print(ptable)
			return ('display_country', 0)
		except Exception as e:
			return ('display_country: {}'.format(str(e)), 500)


	def plot_hist(self):
		try:
			answers = prompt([{'message': 'Choose a criteria :',\
			 'type': 'list', 'name': 'chosen_filter',\
			  'choices': ["superficie", "population", "croissance_demo", "inflation", "dette", "taux_chomage",\
			 "taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]},
			 {'message': 'Choose a year :',\
			 'type': 'list', 'name': 'chosen_year',\
			  'choices': ['Lastest recorded year']+['20%02d'%i for i in range(4,21)]}
			 ], style=self.style)
			tmp_obj = db_handler("factbook")
			sql_q = "select country_name, %s from factbook where country_name IS NOT NULL and country_name!='none' and %s LIKE '%%%s%%';"%(answers['chosen_filter'], answers['chosen_filter'], answers['chosen_year'])
			if answers['chosen_filter']=='superficie':
				sql_q = "select country_name, superficie from factbook where country_name IS NOT NULL and country_name!='none';"
			if answers['chosen_year']=='Lastest recorded year':
				sql_q = "select country_name, %s from factbook where country_name IS NOT NULL and country_name!='none';"%(answers['chosen_filter'])
			resp_ = tmp_obj.sql_run(sql_q)
			data_plt = []
			for j in resp_:
				if j[1]:
					if answers['chosen_year']=='Lastest recorded year':
						re_out = re.findall(r'(-?\d+(\.\d+)?%?)', j[1].split("++")[0].replace(',','')\
							.replace('sq km', ''))
					elif len(re.findall('(\d{4})', j[1])):
						re_out = re.findall(r'(-?\d+(\.\d+)?%?)', [i for i in j[1].split("++") if answers['chosen_year'] in i][0].replace(',','')\
							.replace('sq km', ''))
					else:
						re_out = re.findall(r'(-?\d+(\.\d+)?%?)', j[1].split("++")[0].replace(',','')\
							.replace('sq km', ''))
					if 're_out' in locals() and len(re_out):
						inappend_ = float(re_out[0][0].replace("%",""))
						if 'million' in j[1]:
							inappend_ = inappend_*1e6
						data_plt.append([j[0], inappend_])
			x, y = zip(*data_plt)
			plt.bar(x, y)
			plt.xticks(rotation=90)
			plt.show()
			return ('plot_hist', 0)
		except Exception as e:
			return ('plot_hist: {}'.format(str(e)), 500)


	def plot_boxplot(self):
		try:
			sql_q = "select * from factbook where country_name IS NOT NULL and country_name!='none';"
			tmp_obj = db_handler("factbook")
			resp_ = tmp_obj.sql_run(sql_q)
			main_dict_ = ['0-14 years', '15-24 years', '25-54 years', '55-64 years', '65 years and over']
			tmp_dict_ = {'0-14 years':[], '15-24 years':[], '25-54 years':[], '55-64 years':[], '65 years and over':[]}
			for v in resp_:
				try:
					for key_class in main_dict_:
						s = eval(v[-1])[key_class]['text']
						percent_ = re.findall(r'(-?\d+(\.\d+)%)', s)
						if len(percent_):
							tmp_dict_[key_class].append(float(percent_[0][0].replace('%', '')))
				except:
					pass
			labels, data = [*zip(*tmp_dict_.items())]
			plt.boxplot(data)
			plt.xticks(range(1, len(labels) + 1), labels)
			plt.show()
			return ('plot_boxplot', 0)
		except Exception as e:
			return ('plot_boxplot: {}'.format(str(e)), 500)






	def modify_country(self):
		try:
			country_name_q = [{'message': 'Do you want to :', "type": "list", "name": "addmodify", "choices": ['Add a new country', 'Modify an existent country']},
			 {'filter':lambda val: val.lower(),'message': "What's the name of the country?",'name': 'country_name','type': 'input','validate': AsciiValidator}]
			answersx = prompt(country_name_q, style=self.style)
			tmp_obj = db_handler("factbook")
			resp_ = tmp_obj.sql_run("SELECT * FROM factbook where lower(country_name)=='%s'"%answersx['country_name'])
			if not len(resp_) or answersx['addmodify']=='Modify an existent country':
				temp_resp_ = ['' for i in range(9)]
				if len(resp_):
					temp_resp_ = ['[Current value: %s]'%str(i) for i in resp_[0][2:]]
				country_form = [{'message': 'From which year this data is taken? (press [ENTER] if not exist):','name': 'year','type': 'input','validate': YearValidator}
				, {'message': 'superficie (in square kilometers): '+temp_resp_[0],'name': 'superficie','type': 'input','validate': NumberValidator,\
				"filter": lambda val: val+' sq km'},{'message': 'Population :'+temp_resp_[1],'name': 'population','type': 'input','validate': NumberValidator}
				,{'message': 'Demographic growth (format ex: 34.5%) :'+temp_resp_[2],'name': 'croissance_demo','type': 'input','validate': PercentValidator}
				,{'message': 'inflation (format ex: 2%) :'+temp_resp_[3],'name': 'inflation','type': 'input','validate': PercentValidator}
				,{'message': 'dette (format ex: $45,000,000,000) :'+temp_resp_[4],'name': 'dette','type': 'input','validate': DetteValidator}
				,{'message': 'Unemployement rate (format ex: 20%) :'+temp_resp_[5],'name': 'taux_chomage','type': 'input','validate': PercentValidator}
				,{'message': 'Government expenditure on health (format ex: 20%) :'+temp_resp_[6],'name': 'taux_depense_sante','type': 'input'\
				,'validate': PercentValidator},{'message': 'government expenditure on education (format ex: 20%) :'+temp_resp_[7],\
				'name': 'taux_depense_educ','type': 'input','validate': PercentValidator},
				{'message': 'government expenditure on military (format ex: 20%) :'+temp_resp_[8],'name': 'taux_depense_militaire','type': 'input','validate': PercentValidator}
				,{'message': 'nullx','name': 'nullx','type': 'input','when': lambda answers: print('All good!, Please check later your application status.')}]
				answers = prompt(country_form, style=self.style)
				if len(answers['year']):
					for k_ in self.field_names[2:]:
						answers[k_] += " (%s) ++ "%answers['year']
				sql_input = "INSERT INTO factbook (country_name, superficie, population, croissance_demo, inflation, dette, taux_chomage,\
		 taux_depense_sante, taux_depense_educ, taux_depense_militaire) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"\
					%(answersx["country_name"].capitalize(), answers["superficie"], answers["population"], answers["croissance_demo"],\
					 answers["inflation"], answers["dette"], answers["taux_chomage"], answers["taux_depense_sante"],\
					  answers["taux_depense_educ"], answers["taux_depense_militaire"])
				if answersx['addmodify']=='Modify an existent country':
					sql_input = "UPDATE factbook SET superficie='%s', population='%s',\
					 croissance_demo='%s', inflation='%s', dette='%s', taux_chomage='%s',\
					  taux_depense_sante='%s', taux_depense_educ='%s', taux_depense_militaire='%s' WHERE lower(country_name)=='%s';"%(answers["superficie"],\
					   answers["population"], answers["croissance_demo"],answers["inflation"], answers["dette"],\
						answers["taux_chomage"], answers["taux_depense_sante"],\
				  answers["taux_depense_educ"], answers["taux_depense_militaire"], answersx["country_name"].lower())
				tmp_obj.sql_run(sql_input)
				return ('modify_country', 1)
			else:
				return ('modify_country', 0)
		except Exception as e:
			return ('modify_country: {}'.format(str(e)), 500)


	def review(self):
		try:
			tmp_dict_ = ["country_name", "superficie", "population", "croissance_demo", "inflation", "dette", "taux_chomage","taux_depense_sante", "taux_depense_educ", "taux_depense_militaire"]
			sql_q = "select %s from update_request;"%(','.join(tmp_dict_))
			tmp_obj = db_handler("update_request")
			resp_ = tmp_obj.sql_run(sql_q)
			ptable = PrettyTable()
			ptable.title="Proposed corrections"
			ptable.field_names = tmp_dict_
			if not len(resp_):
				return ('review', 0)
			for k_ in resp_:
				tmp_row = []
				for v in k_:
					try:
						v = v.split("++")[0]
						v = v.replace(re.findall(r'b1x(.*?)b2x', v.replace('(',"b1x").replace(')', 'b2x'))[0], '').replace('()','')
					except:
						pass
					tmp_row.append([v, v[:15]+'...'][0 if len(v)<=20 else 1])
				ptable.add_row(tmp_row)
			print(ptable)
			if not len(resp_):
				return ('review', 0)
			answers = prompt({'type': 'confirm', 'message': 'Do you approve the proposed corrections?', 'name': 'review', 'default': False}, style=self.style)
			if answers['review']:
				for k_ in resp_:
					tmp_obj = db_handler("factbook")
					sql_input = "UPDATE factbook SET superficie='%s', population='%s',\
									 croissance_demo='%s', inflation='%s', dette='%s', taux_chomage='%s',\
									  taux_depense_sante='%s', taux_depense_educ='%s', taux_depense_militaire='%s' WHERE lower(country_name)=='%s';"%\
									  (k_[1], k_[2], k_[3], k_[4], k_[5], k_[6], k_[7], k_[8], k_[9],k_[0].lower())
					tmp_obj.sql_run(sql_input)
			tmp_obj = db_handler("update_request")
			tmp_obj.sql_run("DELETE FROM update_request;")
			return ('review', 1)
		except Exception as e:
			return ('review: {}'.format(str(e)), 500)


	def remove_country(self):
		try:
			countries_lst = [{'message': 'Choose a country to delete:', 'type': 'list', 'name': 'chosen_country', 'choices': []}]
			tmp_obj = db_handler("factbook")
			resp_ = tmp_obj.sql_run("select country_name from factbook where country_name IS NOT NULL and country_name!='none' Order By country_name;")
			countries_lst[0]['choices'] = [i[0] for i in resp_]
			answers = prompt(countries_lst, style=self.style)
			tmp_obj = db_handler("update_request")
			tmp_obj.sql_run("DELETE FROM factbook WHERE country_name=='%s';"%answers['chosen_country'])
			return ('remove_country', 1)
		except Exception as e:
			return ('remove_country: {}'.format(str(e)), 500)


	def remove_account(self):
		try:
			accounts_lst = [{'message': 'Choose an account to delete:', 'type': 'list', 'name': 'chosen_account', 'choices': []}]
			tmp_obj = db_handler("users")
			resp_ = tmp_obj.sql_run("select username from users where privilege IN (1,2);")
			if len(resp_):
				accounts_lst[0]['choices'] = [i[0] for i in resp_]
				answers = prompt(accounts_lst, style=self.style)
				tmp_obj.sql_run("DELETE FROM users WHERE username=='%s';"%answers['chosen_account'])
				return ('remove_account', 1)
			else:
				return ('remove_account', 0)
		except Exception as e:
			return ('remove_account: {}'.format(str(e)), 500)



	def logout(self):
		py = sys.executable
		for k in range(len(sys.argv)):
			if "_Class.py" in sys.argv[k]:
				t = '/' + sys.argv[k]
				t = t[::-1]
				sys.argv[k] = sys.argv[k].replace(t[t.index('_')+1:t.index('/')][::-1]+"_Class.py", 'Consultant_Class.py')
				break
		os.execl(py, py, * sys.argv)


	def sys_exit(self):
		print("[!] Exiting ...")
		sys.exit(0)

if __name__ == "__main__":
	while True:
		try:
			obj_ = AdminClass()
			obj_.generate_menu(0, 1)
		except:
			obj_.generate_menu(3, 1)


