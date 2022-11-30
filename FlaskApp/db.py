import psycopg2, auth
from flask import g, current_app


def CreateInitialSchema(force = False):
	dbconn = GetDatabaseConnection()
	with dbconn.cursor() as cursor:
		if not force:
			cursor.execute("SELECT * FROM pg_tables WHERE schemaname = 'public';")
			if cursor.fetchone() is not None:
				return
		with current_app.open_resource("schema.sql") as schemafile:
			cursor.execute(schemafile.read().decode('utf8'))
		dbconn.commit()
		auth.CreateUser("admin", "password", "create_user,run_test")

def GetDatabaseConnection():
	if 'db' not in g:
		g.db = psycopg2.connect(
			dbname = current_app.config["DBNAME"],
			user = current_app.config["DBUSER"],
			password = current_app.config["DBPASS"],
			host = current_app.config["DBHOST"]
		)
	return g.db

def CloseDatabaseConnection():
	if 'db' in g and g.db is not None:
		g.db.close()
		g.pop('db')