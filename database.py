from flask import g
import sqlite3

def connect_to_database():
	sql = sqlite3.connect('/media/kali/Secyrity/Flask/Employee_management_system/empapp.db')
	sql.row_factory = sqlite3.Row
	return sql

def get_database():
	if not hasattr(g, 'empapp_db'):
		g.empapp_db = connect_to_database() 

	return g.empapp_db
