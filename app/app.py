from crypt import methods
from flask import Flask,render_template, request
import csv
import os 
import pandas as pd
import shutil
import random

app = Flask(__name__)

class Info:
	name = ''
	selected_word = None
	idx = 0
	indexs = None
	word_correct = ''
	word = None
	meaning_correct = ''
	df = None
	index = None

@app.route('/')
def index():
	return render_template('base.html')

@app.route('/name')
def name1():
	return render_template('name.html')

@app.route('/name', methods=['POST'])
def name2():
	name = request.form.get('name')
	file_app(name)
	Info.name = name
	return render_template("nigate.html")

def file_app(name):
	with open('system.csv') as f:
		reader = csv.reader(f)
		l = [row for row in reader]
		l = [list(x) for x in zip(*l)]

	if os.path.exists(f'j2e_{name}.csv'):
		with open(f'j2e_{name}.csv') as f:
			reader = csv.reader(f)
			df = pd.read_csv(f'j2e_{name}.csv')
			Info.df = df
	else:
		shutil.copy('system.csv', f'j2e_{name}.csv')
		df = pd.read_csv(f'j2e_{name}.csv')
		df['rate'] = 0
		df['nums'] = 0
		df['correct_nums'] = 0
		Info.df = df
	return 

"""
@app.route("/nigate", methods=['POST'])
def post2():
	if (request.form.get('normal') != None):
		return render_template("index.html")
	if (request.form.get('nigate') != None):
	   return render_template("index2.html")
	return render_template("index2.html")
"""

@app.route("/nigate", methods=['POST'])
def quiz():
	with open('system.csv') as f:
		reader = csv.reader(f)
		l = [row for row in reader]
		l = [list(x) for x in zip(*l)]
	words = l[1]
	meaning = l[2]
	indexs = []
	for i in range(4):
		indexs.append(random.randint(0, 2026))
	idx = random.randint(0, 3)

	selected_word = []
	selected_meaning = []
	for i in range(4):
		selected_word.append(words[indexs[i]])
		selected_meaning.append(meaning[indexs[i]])
	Info.selected_word = selected_word
	Info.idx = idx
	Info.indexs = indexs

	word_correct = selected_word[idx]
	Info.word_correct = word_correct
	meaning_correct = selected_meaning[idx]
	Info.meaning_correct = meaning_correct

	return render_template("index.html", meaning_correct=meaning_correct, selected_word=selected_word)

@app.route("/index", methods=['POST'])
def quiz2():
	if request.form['send'] == Info.selected_word[0]:
		num = 1
	if request.form['send'] == Info.selected_word[1]:
		num = 2
	if request.form['send'] == Info.selected_word[2]:
		num = 3
	if request.form['send'] == Info.selected_word[3]:
		num = 4
	name = Info.name
	df = Info.df
	idx = Info.idx
	indexs = Info.indexs
	if int(num) - 1 == idx:
		a = '正解!'
		df.iat[indexs[idx]-1, 4] += 1
		df.iat[indexs[idx]-1, 5] += 1
		df.iat[indexs[idx]-1, 3] = df.iat[indexs[idx]-1, 5] / df.iat[indexs[idx]-1, 4] * 100
	else:
		a = f'不正解... 正解は{Info.word_correct}だよ'
		df.iat[indexs[idx]-1, 4] += 1
		df.iat[indexs[idx]-1, 3] = df.iat[indexs[idx]-1, 5] / df.iat[indexs[idx]-1, 4] * 100

	df.to_csv(f'j2e_{name}.csv', index=False)
	return render_template("index.html", meaning_correct=Info.meaning_correct, selected_word=Info.selected_word, a=a)


@app.route("/nigate")
def nigate1():
	with open('system.csv') as f:
		reader = csv.reader(f)
		l = [row for row in reader]
		l = [list(x) for x in zip(*l)]
	words = l[1]
	df = Info.df
	df2 = df[df['nums']>0]
	df2 = df2[df2['rate'] < 60]
	
	try:
		selected = df2.sample()
	except:
		return render_template("nigate.html")

	indexs = []
	for i in range(4):
		indexs.append(random.randint(0, 2026))
	idx = random.randint(0, 3)

	word = selected['words'].values.tolist()[0]
	meaning = selected['meaning'].values.tolist()[0]
	index = selected['index'].values.tolist()[0]
	Info.index = index

	indexs = []
	for i in range(3):
		indexs.append(random.randint(0, 2026))

	selected_word = []
	for i in range(3):
		selected_word.append(words[indexs[i]])

	new_selected = [word] + selected_word
	random.shuffle(new_selected)
	idx = new_selected.index(word)
	Info.word = word
	Info.idx = idx
	Info.meaning_correct = meaning
	Info.selected_word = new_selected
	return render_template("index2.html", meaning_correct=meaning, selected_word=new_selected)

@app.route("/index2", methods=['POST'])
def nigate2():
	idx = Info.idx
	index = Info.index
	df = Info.df
	if request.form['send'] == Info.selected_word[0]:
		num = 1
	if request.form['send'] == Info.selected_word[1]:
		num = 2
	if request.form['send'] == Info.selected_word[2]:
		num = 3
	if request.form['send'] == Info.selected_word[3]:
		num = 4
	if int(num) - 1 == idx:
		a = '正解！'
		df.iat[index-1, 4] += 1
		df.iat[index-1, 5] += 1
		df.iat[index-1, 3] = df.iat[index-1, 5] / df.iat[index-1, 4] * 100
	else:
		a = f'不正解... 正解は{Info.word}だよ'
		df.iat[index-1, 4] += 1
		df.iat[index-1, 3] = df.iat[index-1, 5] / df.iat[index-1, 4] * 100

	df.to_csv(f'j2e_{Info.name}.csv', index=False)
	Info.df = df
	return render_template("index2.html", meaning_correct=Info.meaning_correct, selected_word=Info.selected_word, a=a)

if __name__ == "__main__":
	app.run(debug=True)