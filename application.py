""" application module

A module to manage the exercises application.
"""

import flask
import yaml

import german as g

app = flask.Flask(__name__)

@app.route('/')
def home():

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))
	tables = db.get_tables()

	with open(config.parser['paths'].get('translations'), 'r') as f:
		translations = yaml.full_load(f)

	topics = [
		(t, translations[t])
		if t in translations.keys() else (t, t)
		for t in tables
		]
	
	return flask.render_template(
		'home.html',
		topics = topics,
		)

@app.route('/add_new_topic')
def add_new_topic():

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))

	columns = [
		'table_name',
		'translation',
		]

	for i in range(0, 10):
		columns.append('column_{}'.format(i))

	return flask.render_template(
		'enter.html',
		topic = 'new_topic',
		columns = columns,
		)

@app.route('/return_new_topic', methods = ['POST', 'GET'])
def return_new_topic():

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))

	if flask.request.method == 'POST':
		result = flask.request.form

		with open(config.parser['paths'].get('translations'), 'r') as f:
			translations = yaml.full_load(f)

		translations[result['table_name']] = result['translation']

		with open(config.parser['paths'].get('translations'), 'w') as f:
			yaml.dump(translations, f)

		columns = []
		for key in result.keys():
			if result[key]:
				if 'column' in key:
					columns.append(result[key])

		db.add_table(
			result['table_name'],
			columns = columns,
			)

		another = 'add'
		
		return flask.render_template(
			'return.html',
			next = another,
			result = result,
			topic = 'new_topic',
			)

@app.route('/show_<topic>')
def topic(topic):

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))
	table = g.DataTable(db.get_columns(topic))
	table.add_rows(db.get_rows(topic))

	with open(config.parser['paths'].get('translations'), 'r') as f:
		translations = yaml.full_load(f)
	
	return flask.render_template(
		'data.html',
		title = translations[topic],
		category = topic,
		data = table.to_html(),
		)

@app.route('/add_<topic>')
def add_lexicon(topic):

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))
	columns = db.get_columns(topic)
	columns.remove('id')

	return flask.render_template(
		'enter.html',
		action = 'Add',
		topic = topic,
		columns = columns,
		)

@app.route('/edit_<topic>')
def edit_lexicon(topic):

	columns = [
		'expression',
		'column',
		'value'
		]

	return flask.render_template(
		'enter.html',
		action = 'Edit',
		topic = topic,
		columns = columns,
		)

@app.route('/return_<topic>', methods = ['POST', 'GET'])
def return_topic(topic):

	config = g.Configuration()

	db = g.Database(config.parser['paths'].get('german'))

	if flask.request.method == 'POST':
		result = flask.request.form
		
		if 'meaning' in result.keys():
			db.add_to_table(
				topic,
				list(result.keys()),
				list(result.values())
				)

			another = 'add'

		else:
			columns = db.get_columns(topic)
			db.edit_row(
				table = topic,
				column_search = columns[1],
				value_search = result['expression'],
				column_edit = result['column'],
				value_edit = result['value'],
				)

			another = 'edit'

		return flask.render_template(
			'return.html',
			next = another,
			result = result,
			topic = topic,
			)

if __name__ == '__main__':
   	app.run(debug = True)