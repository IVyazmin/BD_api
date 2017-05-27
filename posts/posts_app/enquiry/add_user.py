from django.db import connection
import psycopg2
from psycopg2.extras import *
from posts_app.enquiry.enquiry import *
from posts_app.enquiry.connect import *

def add_user(user_nickname, forum_slug):
	connect = connectPool()
	cursor = connect.cursor()
	is_user_exist = False
	
	try:
		cursor.execute("INSERT INTO forum_users (user_nickname, forum) VALUES (%s, %s) ON CONFLICT DO NOTHING", [user_nickname, forum_slug])
	except:
		pass
	cursor.close()