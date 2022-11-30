import db
import auth
import json
import datetime
from flask import render_template, Flask, redirect, url_for, session, g, request, flash, session
from flask_bcrypt import Bcrypt
import secrets

app = Flask(__name__)
app.config.from_object('config')

@app.route('/login', methods = ("GET", "POST"))
def login():
    if request.method == "GET":
        if request.args.get('fail'):
            flash("Authentication required!")
            print("Authentication required!")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        if not username:
            error = 'Username is required'
        if error is None:
            if not auth.AuthenticateUser(username, password):
                error = 'Username and password do not match'
            else:
                session["current_user"] = username
                return redirect(url_for('dashboard'))
        if error is not None:
            flash(error)
            print(error)
        
    return render_template('admin_login.html', title='Login')

@app.route('/logout')
def logout():
    session.pop("current_user")
    return redirect(url_for('dashboard'))

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

@app.route('/register')
def register():
    return render_template('admin_signin.html', title='Register')

@app.route('/maintenance', methods = ("GET", "POST"))
@auth.LoginRequired
def maintenance():
    if request.method == "POST":
        if request.form["method"] == "adduser":
            username = request.form["username"]
            password = request.form["password"]
            permissions = request.form["permissions"]
            error = None
            if not username:
                error = 'Username is required'
            else:
                if auth.CheckUserExists(username):
                    error = 'User already exists'
        if error is None:
            auth.CreateUser(username, password, permissions)
            if auth.CheckUserExists(username):
                error = "Account creation successful!"
            else:
                error = "Account creation failed!"
        if error is not None:
            flash(error)
            print(error)
    return render_template('maintenance.html', title='Maintenance', user = session["current_user"], auth = auth) 

@app.route('/')
def dashboard():
    initSensorState(session)
    print(session)
    return render_template('dashboard.html', title='Dashboard')

@app.route('/dashboard')
def dashboard1():
    return render_template('dashboard.html', title='Dashboard', data=session)

def initSensorState(sesh):
    print("inside init state")
    sesh['Brd1-Ceiling'] = 'off'
    sesh['Brd2-Ceiling'] = 'off'
    sesh['Brd3-Ceiling'] = 'off'

    sesh['Brd1-Lamp1'] = 'off'
    sesh['Brd1-Lamp2'] = 'off'
    sesh['Brd2-Lamp1'] = 'off'
    sesh['Brd2-Lamp2'] = 'off'
    sesh['Brd3-Lamp1'] = 'off'
    sesh['Brd3-Lamp2'] = 'off'

    sesh['Living-Room-Ceiling'] = 'off'
    sesh['Bathroom1'] = 'off'
    sesh['Living-Room-Lamp1'] = 'off'
    sesh['Living-Room-Lamp2'] = 'off'
    sesh['Bathroom2'] = 'off'
    sesh['Kitchen-Lamp'] = 'off'

@app.route('/report')
def reporting():
    return render_template('reporting.html', title='Reporting')

@app.route('/setState/<sensor>')
def setState(sensor):
    print("Sensor: ", sensor)
    if session[sensor] == 'on':
        session[sensor] = 'off'
    else:
        session[sensor] = 'on'
    print(sensor + ": " + session[sensor])
    return render_template('dashboard.html', title='Dashboard')

@app.route('/reporting/rest/getPowerUsage')
def getPowerUsage():
    with db.GetDatabaseConnection() as dbconn:
        with dbconn.cursor() as cursor:
            startTime = datetime.datetime.now() - datetime.timedelta(days=62)
            print("Start Time: ", startTime)
            cursor.execute("SELECT time, SUM(value::Numeric) FROM SensorEvent, Sensor WHERE time >= (%s) AND SensorEvent.sensor_id = Sensor.sensor_id AND category='power' GROUP BY time ORDER BY time;", (startTime,))
            data = cursor.fetchall()
            if data is not None:
                return data
            else:
                return json.dumps([])

@app.route('/reporting/rest/getWaterUsage')
def getWaterUsage():
    with db.GetDatabaseConnection() as dbconn:
        with dbconn.cursor() as cursor:
            startTime = datetime.datetime.now() - datetime.timedelta(days=62)
            cursor.execute("SELECT time, SUM(value::Numeric) FROM SensorEvent, Sensor WHERE time >= (%s) AND SensorEvent.sensor_id = Sensor.sensor_id AND category='water' GROUP BY time ORDER BY time;",(startTime,))
            data = cursor.fetchall()
            if data is not None:
                return data
            else:
                return json.dumps([])

app.secret_key = secrets.token_hex(16)
app.config.from_object('config')

def main():
    with app.app_context():
        db.CreateInitialSchema(False)
        app.run(debug=True)

# can't check __name__ because it breaks flask run
if __name__ == "__main__":
    main()
