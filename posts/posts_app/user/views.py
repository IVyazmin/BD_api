from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
from posts_app.enquiry.connect import *
import psycopg2
from django.db.utils import IntegrityError, DatabaseError

@csrf_exempt
def create(request, nickname):
	body = loads(request.body.decode('utf8'))
	about = body['about']
	email = body['email']
	fullname = body['fullname']

	connect = connectPool()
	cursor = connect.cursor()
	is_user_exist = False
	param_array = ["about", "email", "fullname", "nickname"]
	try:
		cursor.execute(INSERT_USER, [about, email, fullname, nickname])
	except:
		is_user_exist = True
	if is_user_exist:
		users = []
		cursor.execute(SELECT_USERS_BY_EMAIL_OR_NICKNAME, [email, nickname])
		for user in cursor.fetchall():
			users.append(dict(zip(param_array, user)))
		cursor.close()
		
		return JsonResponse(users, status = 409, safe = False)
	else:
		cursor.close()
		
		body['nickname'] = nickname
		return JsonResponse(body, status = 201)

@csrf_exempt
def profile(request, nickname):
	if request.method == 'POST':
		connect = connectPool()
		cursor = connect.cursor()
		cursor.execute(SELECT_USER_BY_NICKNAME, [nickname,])
		if cursor.rowcount == 0:
			cursor.close()
			
			return JsonResponse({}, status = 404)
		user = cursor.fetchone()
		param_array = ["about", "email", "fullname", "nickname"]
		user = dict(zip(param_array, user))
		body = loads(request.body.decode('utf8'))
		if 'about' in body:
			user['about'] = body['about']
		if 'email' in body:
			user['email'] = body['email']
		if 'fullname' in body:
			user['fullname'] = body['fullname']
		user['nickname'] = nickname
		try:
			cursor.execute(UPDATE_USER, [user['about'], user['email'], user['fullname'], user['nickname']])
		except:
			cursor.close()
			
			return JsonResponse({}, status = 409)
		cursor.close()
		
		return JsonResponse(user, status = 200)
	else:
		connect = connectPool()
		cursor = connect.cursor()
		cursor.execute(SELECT_USER_BY_NICKNAME, [nickname,])
		if cursor.rowcount == 0:
			cursor.close()
			
			return JsonResponse({}, status = 404)
		user = cursor.fetchone()
		cursor.close()
		
		param_array = ["about", "email", "fullname", "nickname"]
		user = dict(zip(param_array, user))
		return JsonResponse(user, status = 200)
	