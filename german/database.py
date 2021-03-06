""" database module

A module to manage a database.
"""

import sqlite3 as sql
import pandas as pd
import os

import german as g

class Database(object):
	"""
	A class that represents a database.

	Attributes
	----------
	path : string
		The path to the database file.
	connection : sqlite3.connection
		The connection to the database.
	cursor : sqlite3.cursor
		The cursor of the database.
	"""

	def __init__(self, path):
		
		self.path = path
		self.connection = sql.connect(path)
		self.cursor = self.connection.cursor()

	def get_tables(self):
		"""
		Returns a list with all the tables in the database.

		Returns
		----------
		list
			The tables in the database.
		"""

		self.cursor.execute(
			"SELECT name FROM sqlite_master WHERE type='table';"
			)
		tables = self.cursor.fetchall()
		tables = [item for sublist in tables for item in sublist]
		tables.sort()

		return tables

	def add_table(self, name, columns):
		"""
		Adds the verbs table to the database.

		Parameters
		----------
		name : string
			The name of the table.
		columns : list
			The columns of the table.
		"""

		table = 'CREATE TABLE IF NOT EXISTS {}'.format(name)

		columns = [c + ' text' for c in columns]
		columns.insert(0, 'id integer PRIMARY KEY')
		columns[1] = columns[1] + ' NOT NULL'
		cols = ','.join(columns)

		command = '{} ({})'.format(table, cols)

		self.cursor.execute(command)
		self.connection.commit()

	def table_to_dataframe(self, table):
		"""
		Transforms a table into a pandas.DataFrame

		Parameters
		----------
		table : string
			The name of the table.

		Return
		----------
		pandas.DataFrame
			A DataFrame containing the data from the table.
		"""

		command = 'SELECT * FROM {}'.format(table)
		df = pd.read_sql_query(command,
			self.connection,
			index_col = 'id',
			)

		return df

	def add_to_table(self, table, columns, values):
		"""
		Adds a row to the table.

		Parameters
		----------
		table : string
			The name of the table.
		columns : list
			The columns of the table.
		values : list
			The values to add to the table.
		"""		
		
		if 'sort_value' in self.get_columns(table, sv = True):
			columns.append('sort_value')
			values.append(g.get_sort_value(values[0]))

		tab = 'INSERT INTO {}'.format(table)
		cols = ','.join(columns)
		vals = ','.join(['?' for c in columns])

		command = '{} ({}) VALUES ({})'.format(tab, cols, vals)

		self.cursor.execute(command, values)
		self.connection.commit()

		self.dump_table(table)

	def add_sort_value(self, table, column = None):
		"""
		Adds a column that is used for sorting. Sort without articles
		and umlauts.
		"""

		try:
			command = "ALTER TABLE {} ADD COLUMN {} text".format(
				table,
				'sort_value',
				)
			self.cursor.execute(command)
		except sql.OperationalError:
			pass

		if column == None:
			column = self.get_columns(table, id = True)[1]

		rows = self.get_rows(table, id = True)

		for row in rows:
			sort_value = g.get_sort_value(row[column])
			command = "UPDATE {} SET {} = '{}' WHERE Id = {}".format(
			table,
			'sort_value',
			sort_value,
			row['id'],
			)
			self.cursor.execute(command)

		self.connection.commit()
		self.dump_table(table)

	def get_columns(self, table, id = False, sv = False):
		"""
		Returns the columns of a table.

		Parameters
		----------
		table : string
			The name of the table.
		id : boolean
			Whether to return or not the id.
		sv : boolean
			Whether to return or not the sort_value.

		Returns
		----------
		list
			The columns of the table.
		"""

		self.cursor.execute('PRAGMA table_info({})'.format(table))
		columns = [c[1] for c in self.cursor.fetchall()]

		if not sv:
			if 'sort_value' in columns:
				columns.remove('sort_value')
		if not id:
			if 'id' in columns:
				columns.remove('id')
		
		return columns

	def get_rows(self, table, sort_by = None, id = False, sv = False):
		"""
		Returns the rows of a table.

		Parameters
		----------
		table : string
			The name of the table.
		id : boolean
			Whether to return or not the id.
		sv : boolean
			Whether to return or not the sort_value.
		sort_by : string
			How to sort the values

		Returns
		----------
		list
			The rows of the table.
		"""

		columns = self.get_columns(table, id = True, sv = True)
		if sort_by == 'module':
			sort_value = 'module DESC, category ASC, sort_value ASC'
		else:
			if 'sort_value' in columns:
				sort_value = 'sort_value'
			else:
				sort_value = 'id'

		self.cursor.execute(
			'SELECT * FROM {} ORDER BY {}'.format(table, sort_value)
			)
		rows = self.cursor.fetchall()

		rows = [{k:v for k,v in zip(columns, row)} for row in rows]

		if not id:
			rows = [
				{k: v for k, v in row.items() if k != 'id'}
			 	for row in rows
				 ]
		if not sort_value:
			rows = [
				{k: v for k, v in row.items() if k != 'sort_value'}
				for row in rows
				]
		
		return rows

	def edit_row(
		self,
		table,
		column_search,
		value_search,
		column_edit,
		value_edit
		):
		"""
		Edits one row of the table.

		Attributes
		----------
		table : string
			The name of the table.
		column_search : string
			The column to search.
		value_search : string
			The value to search.
		column_edit : string
			The column to edit.
		value_edit : string
			The value to edit.
		"""

		command = "SELECT * FROM {} WHERE {} = '{}'".format(
			table,
			column_search,
			value_search,
			)
		self.cursor.execute(command)
		row = self.cursor.fetchone()
		row_id = row[0]

		command = "UPDATE {} SET {} = '{}' WHERE Id = {}".format(
			table,
			column_edit,
			value_edit,
			row_id,
			)
		self.cursor.execute(command)
		self.connection.commit()

		self.dump_table(table)

	def dump(self):
		"""
		Dumps the database into a .csv files.
		"""

		config = g.Configuration()
		filename_base = config.parser['paths'].get('dump')

		for table in self.get_tables():
			self.dump_table(table)

	def dump_table(self, table):
		"""
		Dumps a table from the database into a .csv file.

		Parameters
		----------
		table : string
			The name of the table to dump.
		"""

		config = g.Configuration()
		filename_base = config.parser['paths'].get('dump')

		df = self.table_to_dataframe(table)
		filename = '{}{}.csv'.format(filename_base, table)
		df.to_csv(filename, encoding = 'utf-8-sig')