import functools
from flask import session, g, current_app, redirect, url_for
from flask_bcrypt import Bcrypt
import db

def GetBcrypt():
	if "bcrypt" not in g:
		g.bcrypt = Bcrypt(current_app)
	return g.bcrypt

def CheckUserExists(username):
	user_exists = False
	with db.GetDatabaseConnection() as dbconn:
		with dbconn.cursor() as cursor:
			cursor.execute("SELECT name FROM appuser WHERE name = (%s)", (username,))
			user_exists = cursor.fetchone() is not None
	return user_exists

def CreateUser(username, password, permissions = None):
	if CheckUserExists(username):
		return False
	with db.GetDatabaseConnection() as dbconn:
		with dbconn.cursor() as cursor:
			passhash = GetBcrypt().generate_password_hash(password).decode('utf-8')
			cursor.execute("INSERT INTO appuser (name, permissions, password) VALUES (%s, %s, %s)", (username, permissions, passhash))
		dbconn.commit()
	return True

def AuthenticateUser(username, password):
	if not CheckUserExists(username):
		return False
	is_authenticated = False
	with db.GetDatabaseConnection() as dbconn:
		with dbconn.cursor() as cursor:
			cursor.execute("SELECT password FROM appuser WHERE name = (%s)", (username,)) # this is fine, it's just the hash
			passhash = cursor.fetchone()
			passhash = passhash[0]
			if passhash is not None:
				is_authenticated = GetBcrypt().check_password_hash(passhash, password) # authenticated if password matches
			else:
				if password: # If you provide a password when there is none, it's wrong!
					is_authenticated = False
				else:
					is_authenticated = True # user has no password
	return is_authenticated

# decorator for a view that checks session authentication
def LoginRequired(view):
	@functools.wraps(view)
	def view_decorator(**kwargs):
		if 'current_user' not in session: # no user?
			return redirect(url_for('login', fail = True)), 302 # must use 302 to redirect instead of 401
		return view(**kwargs) # use current arguments
	return view_decorator

# We assume that the permissions field, if it's set, is a comma-separated list of provided permission names.
def HasPermissions(username, permissions):
	# false if we're missing any of the permissions
	return not any(GetMissingPermissions(username, permissions))

def GetMissingPermissions(username, permissions):
	wanted_permissions = permissions.split(',')
	if not wanted_permissions:
		return None
	if not CheckUserExists(username):
		return None
	with db.GetDatabaseConnection() as dbconn:
		with dbconn.cursor() as cursor:
			cursor.execute("SELECT permissions FROM appuser WHERE name = (%s)", (username,))
			(user_permission_string, ) = cursor.fetchone()
			if not user_permission_string:
				return wanted_permissions
			user_permissions = user_permission_string.split(',')
			return [perm for perm in wanted_permissions if perm not in user_permissions]