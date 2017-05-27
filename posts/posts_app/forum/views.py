from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection, DatabaseError, IntegrityError
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
from posts_app.enquiry.connect import *
from posts_app.enquiry.add_user import *
import pytz

@csrf_exempt
def create_forum(request):
	body = loads(request.body.decode('utf8'))
	slug = body['slug']
	title = body['title']
	user_nickname = body['user']

	connect = connectPool()
	cursor = connect.cursor()
	is_forum_exist = False
	cursor.execute(SELECT_USER_BY_NICKNAME, [user_nickname,])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	user_nickname = cursor.fetchone()[3]
	try:
		cursor.execute(INSERT_FORUM, [slug, title, user_nickname])
	
	except:
		is_forum_exist = True
	if is_forum_exist:
		cursor.execute(SELECT_FORUM_BY_SLUG, [slug,])
		exist_forum = cursor.fetchone()
		param_array = ["posts", "slug", "threads", "title", "user"]
		exist_forum = dict(zip(param_array, exist_forum))
		cursor.close()
		
		return JsonResponse(exist_forum, status = 409)
	else:
		cursor.close()
		
		body['user'] = user_nickname
		return JsonResponse(body, status = 201)

@csrf_exempt
def create_thread(request, forum_slug):
	body = loads(request.body.decode('utf8'))
	user_nickname = body['author']
	message = body['message']
	if 'slug' in body:
		slug = body['slug']
	else:
		slug = None
	if 'created' in body:
		created = body['created']
	title = body['title']

	connect = connectPool()
	cursor = connect.cursor()
	cursor.execute(SELECT_USER_BY_NICKNAME, [user_nickname,])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	user_nickname = cursor.fetchone()[3]
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	forum_slug = cursor.fetchone()[1]
	is_thread_exist = False
	if 'created' in body:
		try:
			cursor.execute(INSERT_THREAD, [user_nickname, created, forum_slug, message, slug, title])
			body['id'] = cursor.fetchone()[0]
		except:
			is_thread_exist = True
	else:
		try:
			cursor.execute(INSERT_THREAD_NOW, [user_nickname, forum_slug, message, slug, title])
			body['id'] = cursor.fetchone()[0]
		except:
			is_thread_exist = True
	if is_thread_exist:
		cursor.execute(SELECT_THREAD_BY_SLUG_ALL, [slug,])
		param_array = ["author", "created", "forum", "id", "message", "slug", "title", "votes"]
		exist_thread = cursor.fetchone()
		exist_thread = dict(zip(param_array, exist_thread))
		cursor.close()
		
		exist_thread['created'] = localtime(exist_thread['created'])
		return JsonResponse(exist_thread, status = 409)
	else:
		body['forum'] = forum_slug
		cursor.execute(PLASS_THREAD, [forum_slug,])
		cursor.close()
		add_user(user_nickname, forum_slug)
		return JsonResponse(body, status = 201)

def details(request, forum_slug):
	connect = connectPool()
	cursor = connect.cursor()
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	forum = cursor.fetchone()
	cursor.close()
	
	param_array = ["posts", "slug", "threads", "title", "user"]
	user = dict(zip(param_array, forum))
	return JsonResponse(user, status = 200)

def threads(request, forum_slug):
	connect = connectPool()
	cursor = connect.cursor()
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	limit = ' ALL '
	if 'limit' in request.GET:
		limit = request.GET['limit']
	order = 'asc'
	if 'desc' in request.GET:
		order = 'desc' if request.GET['desc'] == 'true' else 'asc'
	since = ''
	if 'since' in request.GET:
		znak = ' <= ' if order == 'desc' else ' >= '
		since = 'and created ' + znak + "'" +request.GET['since'] + "'"

	order = ' ' + order + ' '
	forum_slug = "'" + forum_slug + "'"

	query = SELECT_THREADS_BY_FORUM % (forum_slug, since, order, limit)
	cursor.execute(query)

	threads = []
	param_array = ['author', 'created', 'forum', 'id', 'message', 'slug', 'title', 'votes']
	for thread in cursor.fetchall():
		thread = list(thread)
		thread[1] = localtime(thread[1])
		threads.append(dict(zip(param_array, thread)))
	cursor.close()
	
	return JsonResponse(threads, status = 200, safe = False)

def localtime(created):
	timezone = pytz.timezone('Europe/Moscow')
	return created.astimezone(timezone)

def users(request, forum_slug):
	connect = connectPool()
	cursor = connect.cursor()
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	args = []
	order = ' asc '
	znak = '> '
	whereN = ' where '
	since = ''
	limit = ''
	forum_slug = "'" + forum_slug + "'"
	if cursor.rowcount == 0:
		cursor.close()
		
		return JsonResponse({}, status = 404)
	if 'desc' in request.GET:
		if request.GET['desc'] == 'true':
			order = ' desc '
			znak = '< '
	if 'since' in request.GET:
		since = "'" + request.GET['since'] + "'"
		whereN += 'nickname ' + znak + since + ' and '
	else:
		znak = ''


	if 'limit' in request.GET:
		limit = 'limit ' + str(request.GET['limit'])
	
	query = SELECT_USERS_BY_FORUM % (whereN, forum_slug, order, limit)
	cursor.execute(query)
	
	param_array = ["about", "email", "fullname", "nickname"]
	users = [dict(zip(param_array, user)) for user in cursor.fetchall()]
	cursor.close()
	
	return JsonResponse(users, status = 200, safe = False)