# coding: utf8

from dbhandler import db_handler
import json


class factbook_processor:
	def __init__(self):
		self.asset_endpoint_ = 'assets'
		self.db_name = 'factbook-country-profiles.json'


	def insert_db(self):
		self.db_dic = []
		with open('%s/%s'%(self.asset_endpoint_, self.db_name),'r') as f:
			data = json.loads(f.read())
		js_struct = {"country_name":"['Government']['Country name']['conventional short form']['text']", "superficie":"['Geography']['Area']['total']['text']", "population":"['People and Society']['Population']['text']", "croissance_demo":"['People and Society']['Population growth rate']['text']", "inflation":"['Economy']['Inflation rate (consumer prices)']['text']", "dette":"['Economy']['Debt - external']['text']", "taux_chomage":"['Economy']['Unemployment rate']['text']", "taux_depense_sante":"['People and Society']['Health expenditures']['text']", "taux_depense_educ":"['People and Society']['Education expenditures']['text']", "taux_depense_militaire":"['Military and Security']['Military expenditures']['text']", "classes_age":"['People and Society']['Age structure']"}
		tmp_columns = ('country_name', 'superficie', 'population', 'croissance_demo', 'inflation', 'dette', 'taux_chomage', 'taux_depense_sante', 'taux_depense_educ', 'taux_depense_militaire', 'classes_age')
		for indx in data:
			db_row = []
			for indx_j in range(len(tmp_columns)):
				try:
					db_row.append(str(eval("indx"+js_struct[tmp_columns[indx_j]])))
				except:
					db_row.append(None)
			self.db_dic.append(db_row)
		tmp_obj = db_handler("factbook")
		tmp_obj.batch_insert(tmp_columns, self.db_dic)
		return self.db_dic


if __name__ == "__main__":
	obj_ = factbook_processor()
	obj_.insert_db()