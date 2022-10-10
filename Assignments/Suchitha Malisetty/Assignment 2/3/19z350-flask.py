from flask import Flask, redirect, url_for, request
app = Flask(_name_)


@app.route('/success/<name>')
def success(name):
	return 'HELLO %s!' % name


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		user = request.form['name']
		return redirect(url_for('success', name=user))
	else:
		user = request.args.get('name')
		return redirect(url_for('success', name=user))


if _name_ == '_main_':
	app.run(debug=True)
