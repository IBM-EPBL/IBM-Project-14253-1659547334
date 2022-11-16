from flask import Flask, render_template, request, redirect, url_for, session
import os
import re
import ibm_db
import sendgrid

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31498;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vvx91242;PWD=890AAUb5jH6gu8T5",'','')


app = Flask(__name__)
app.secret_key=os.urandom(12)

@app.route('/', methods =['GET', 'POST'])
def home():
	return redirect(url_for('login'))

@app.route('/dash', methods =['GET', 'POST'])
def dash():
	if request.method == 'GET':
		return render_template('home.html')


@app.route('/login', methods =['GET', 'POST'])
def login():
	msg=''
	if request.method == 'GET':
		return render_template('login.htm')
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		sql="SELECT * FROM VVX91242.USER WHERE USER_NAME='"+username+"'AND PASSWORD='"+password+"'"
		stmt= ibm_db.exec_immediate(conn,sql)
		account= ibm_db.fetch_assoc(stmt)
		if account:
			session['loggedin'] = True
			session['id'] = account['USER_ID']
			session['username'] = account['USER_NAME']
			msg = 'Logged in successfully !'
			return render_template('dashboard.html', msg = username)

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg=''
	if request.method == 'GET':
		return render_template('register.html')
		
	if request.method == 'POST'  and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		print(request.form)
		sql="SELECT * FROM VVX91242.USER WHERE USER_NAME='"+username+"'"
		stmt= ibm_db.exec_immediate(conn,sql)
		account= ibm_db.fetch_assoc(stmt)
		if account:
			msg = 'Account already exists !'
			return render_template('register.html', msg = msg)
		else:
			sql="INSERT INTO VVX91242.USER(USER_ID,"'USER_NAME'","'PASSWORD'","'EMAIL'") VALUES(seq_person.nextval,'"+username+"','"+password+"','"+email+"')"
			stmt= ibm_db.exec_immediate(conn,sql)
			msg = 'You have successfully registered !'
			return render_template('login.htm', msg = msg)

@app.route('/add_items', methods =['GET', 'POST'])
def add_items():
	msg=''
	if request.method == 'GET':
		return render_template('add_items.html')
	if request.method == 'POST':
		product_name = request.form['name']
		supplier = request.form['supplier']
		threshold = request.form['t_quantity']
		sql="INSERT INTO VVX91242.PRODUCT_DETAILS(PRODUCT_ID,"'PRODUCT_NAME'","'SUPPLIER'",QUANTITY,THRESHOLD_QTY) VALUES(product_seq.nextval,'"+product_name+"','"+supplier+"',0,"+threshold+")"
		stmt= ibm_db.exec_immediate(conn,sql)
		#msg = 'Product successfully added !'
		return render_template('add_items.html', msg = msg)

@app.route('/delete_items', methods =['GET', 'POST'])
def delete_items():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM VVX91242.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			print(product_details)
		return render_template('delete_items.html',product_details=product_details)
	
@app.route('/delete_selected_stocks/<product_id>', methods =['GET', 'POST'])
def delete_selected_stocks(product_id):
	if request.method == 'GET':
		sql="DELETE FROM VVX91242.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		return redirect(url_for('delete_items'))

@app.route('/add_stocks', methods =['GET', 'POST'])
def add_stocks():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM VVX91242.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			print(product_details)
		return render_template('add_stocks.html',product_details=product_details)

@app.route('/add_selected_stocks/<product_id>', methods =['GET', 'POST'])
def add_selected_stocks(product_id):
	if request.method == 'GET':
		return render_template('add_quantity.html',product_id=product_id)
	if request.method == 'POST':
		quantity = int(request.form['quantity'])
		location = request.form['location']
		dop = request.form['dop']
		sql="SELECT quantity,product_name FROM VVX91242.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		qty= ibm_db.fetch_assoc(stmt)
		quantity+=qty['QUANTITY']
		product_name=qty['PRODUCT_NAME']
		sql="UPDATE PRODUCT_DETAILS SET QUANTITY ="+str(quantity)+" WHERE PRODUCT_ID="+product_id+";"
		stmt= ibm_db.exec_immediate(conn,sql)
		sql="INSERT INTO VVX91242.PRODUCT_ADD_DETAILS(ADD_ID,PRODUCT_ID,"'PRODUCT_NAME'","'LOCATION'",QUANTITY,"'DATE_OF_PURCHASE'") VALUES(add_seq.nextval,"+product_id+",'"+product_name+"','"+location+"',"+str(quantity)+",'"+request.form['dop']+"')"
		stmt= ibm_db.exec_immediate(conn,sql)
		# msg = 'Product successfully added !'
		return redirect(url_for('add_stocks'))

@app.route('/update_stocks', methods =['GET', 'POST'])
def update_stocks():
	msg=''
	product_details=[]
	if request.method == 'GET':
		sql="SELECT * FROM VVX91242.PRODUCT_DETAILS"
		stmt= ibm_db.exec_immediate(conn,sql)
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			data['quantity']=ibm_db.result(stmt,2)
			data['supplier']=ibm_db.result(stmt,3)
			product_details.append(data)
			# msg = 'You have successfully registered !'
			
		return render_template('update_stocks.html',product_details=product_details)

@app.route('/update_selected_stocks/<product_id>', methods =['GET', 'POST'])
def update_selected_stocks(product_id):
	product_details=[]
	if request.method == 'GET':
		return render_template('update_quantity.html',product_id=product_id)
	if request.method == 'POST':
		quantity = int(request.form['quantity'])
		sql="SELECT quantity,product_name FROM VVX91242.PRODUCT_DETAILS WHERE PRODUCT_ID="+product_id
		stmt= ibm_db.exec_immediate(conn,sql)
		qty= ibm_db.fetch_assoc(stmt)
		new_quantity=int(qty['QUANTITY']-quantity)
		sql="UPDATE PRODUCT_DETAILS SET QUANTITY ="+str(new_quantity)+" WHERE PRODUCT_ID="+product_id+";"
		stmt= ibm_db.exec_immediate(conn,sql)
		sql="SELECT product_id,product_name FROM VVX91242.PRODUCT_DETAILS WHERE VVX91242.PRODUCT_DETAILS.QUANTITY<=THRESHOLD_QTY"
		stmt= ibm_db.exec_immediate(conn,sql)
		strr="Items below threshold\n"
		i=1
		while ibm_db.fetch_row(stmt) != False:
			data={}
			data['Product_ID']=ibm_db.result(stmt,0)
			data['Product_name']=ibm_db.result(stmt,1)
			strr+=str(i)+". "+data['Product_name']+"\n"
			i+=1
		product_details.append(data)

		print(product_details)
		return redirect(url_for('update_stocks'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
	
if __name__ == '__main__':
	app.run(debug=True)



