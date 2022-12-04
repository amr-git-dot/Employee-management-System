from flask import Flask, url_for, request, redirect, session, g
from flask.templating import render_template
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
	if hasattr(g, 'empapp_db'):
		g.empapp_db.close()


def get_current_user():
	user = None
	if 'user' in session:
		user = session['user']
		db =get_database()
		user_data = db.execute('select * from users where name = ?',[user])
		user = user_data.fetchone()
	return user
		

@app.route('/')
def index():
	user = get_current_user()
	return render_template('home.html', user = user)

@app.route('/login', methods=["POST", "GET"])
def login():
	user = get_current_user()
	error = None
	db = get_database()
	if request.method == "POST":
		name = request.form['name']
		password = request.form['password']
		user_data = db.execute('select * from users where name = ?',[name])
		user = user_data.fetchone()

		if user:
			if check_password_hash(user['password'], password):
				session['user'] = user['name']
				return redirect(url_for('dashboard'))
			else:
				error = "wrong credintials"
		else:
			error = "wrong credintials"

	return render_template('login.html', loginerror = error, user = user)

@app.route('/register', methods=["POST", "GET"])
def register():
	user = get_current_user()
	error = None
	db = get_database()

	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		hashed_password = generate_password_hash(password)
		Registerd_users = db.execute('select * from users where name = ?', [name])
		user_exist = Registerd_users.fetchone()
		if user_exist:
			error = "user already exist"
			return render_template('register.html', registererror = error)

		db.execute('insert into users (name,password) values (?, ?)', [name,hashed_password])
		db.commit()
		return redirect(url_for('login'))
	return render_template('register.html',user = user)

@app.route('/dashboard')
def dashboard():
	user = get_current_user()
	db = get_database()
	emp_data = db.execute('select * from emp')
	employees = emp_data.fetchall()

	return render_template('dashboard.html', user = user, employees = employees)

@app.route('/addnewemployee', methods= ["POST","GET"])
def addnewemployee():
	user = get_current_user()
	db = get_database()
	done = None
	if request.method == "POST":
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		address = request.form['address']
		db.execute('insert into emp (name, email, phone, address) values (?, ?, ?, ?)',[name, email, phone, address])
		db.commit()
		done = "user inserted successfully"
		return render_template('addnewemployee.html',user = user,done = done)
	return render_template('addnewemployee.html',user = user)

@app.route('/singleemployee/<int:empid>')
def singleemployee(empid):
	user = get_current_user()
	db = get_database()
	emp_data = db.execute('select * from emp where empid = ?', [empid])
	single_emp = emp_data.fetchone()
	return render_template('singleemployee.html', user = user, single_emp = single_emp)

@app.route('/fetchemp/<int:empid>')
def fetchemp(empid):
	user = get_current_user()
	db = get_database()
	emp_data = db.execute('select * from emp where empid = ?', [empid])
	single_emp = emp_data.fetchone()
	return render_template('updateemployee.html', user = user, single_emp = single_emp)


@app.route('/updateemployee', methods=["POST", "GET"])
def updateemployee():
	user = get_current_user()
	if request.method == "POST":
		db = get_database()
		empid = request.form['id']
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		address = request.form['address']
		db.execute('update emp set name = ?, email = ?, phone = ?, address = ? where empid = ?',[name, email, phone, address, empid])
		db.commit()
		return redirect(url_for('dashboard', user = user))
#	return render_template('updateemployee.html', user= user)

@app.route('/deleteemployee/<int:empid>')
def deleteemployee(empid):
	user = get_current_user()
	db = get_database()
	db.execute('delete from emp where empid = ?', [empid])
	db.commit()
	return redirect(url_for('dashboard', user = user))

#there is a problem here
@app.route('/logout')
def logout(): 
	session.pop('user', None)
	render_template('home.html')







if __name__ == '__main__': 
	app.run(debug = True)