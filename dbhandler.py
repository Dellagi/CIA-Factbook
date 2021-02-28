import sqlite3,json

class db_handler:

	def __init__(self, table):
		self.db_name = 'assets/main.db'
		self.table_ = table
		with open("assets/db_tables.txt") as f:
			sql_cmd_pack = eval(f.read())[table]
			if type(sql_cmd_pack)==type([]):
				for single_query in sql_cmd_pack:
					if "INSERT" in single_query:
						try:
							if len(self.sql_run("SELECT * FROM users;")):
								break
						except:
							pass
					self.sql_run(single_query)
			else:
				self.sql_run(sql_cmd_pack)

	def sql_run(self, cmd):
		sql = sqlite3.connect(self.db_name)
		sql_cursor = sql.cursor()
		sql_cursor.execute(cmd)
		dbmsg = 0
		try:
			dbmsg = sql_cursor.fetchall()
		except:
			dbmsg = sql_cursor.fetchone()
		sql.commit()
		sql_cursor.close()
		sql.close()
		return dbmsg

	def batch_insert(self, columns, db_dic):
		base_ = "INSERT INTO {} ({}) VALUES ".format(self.table_, db_dic)
		con = sqlite3.connect(self.db_name)
		sql_cursor = con.cursor()
		sql_cursor.executemany("INSERT INTO factbook (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"%','.join(columns), db_dic)
		con.commit()
		con.close()



