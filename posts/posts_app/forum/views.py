from django.views.decorators.csrf import csrf_exempt
from json import loads
from django.db import connection, DatabaseError, IntegrityError
from django.http import JsonResponse
from posts_app.enquiry.enquiry import *
import pytz

@csrf_exempt
def create_forum(request):
	body = loads(request.body.decode('utf8'))
	slug = body['slug']
	title = body['title']
	user_nickname = body['user']

	cursor = connection.cursor()
	is_forum_exist = False
	cursor.execute(SELECT_USER_BY_NICKNAME, [user_nickname,])
	if cursor.rowcount == 0:
		cursor.close()
		return JsonResponse({}, status = 404)
	user_nickname = cursor.fetchone()[3]
	try:
		cursor.execute(INSERT_FORUM, [slug, title, user_nickname])
	
	except IntegrityError:
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

	cursor = connection.cursor()
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
		except IntegrityError:
			is_thread_exist = True
	else:
		try:
			cursor.execute(INSERT_THREAD_NOW, [user_nickname, forum_slug, message, slug, title])
			body['id'] = cursor.fetchone()[0]
		except IntegrityError:
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
		return JsonResponse(body, status = 201)

def details(request, forum_slug):
	cursor = connection.cursor()
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
	cursor = connection.cursor()
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	if cursor.rowcount == 0:
		cursor.close()
		return JsonResponse({}, status = 404)
	limit = 99999999
	if 'limit' in request.GET:
		limit = request.GET['limit']
	order = False
	if 'desc' in request.GET:
		order = True if request.GET['desc'] == 'true' else False
	since = '3001.01.01'
	if 'since' in request.GET:
		since = request.GET['since']
	if order:
		cursor.execute(SELECT_THREADS_BY_FORUM_DESC, [forum_slug, since, limit])
	else:
		if 'since' not in request.GET:
			since = '0001.01.01'
		cursor.execute(SELECT_THREADS_BY_FORUM_ASC, [forum_slug, since, limit])
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
	cursor = connection.cursor()
	cursor.execute(SELECT_FORUM_BY_SLUG, [forum_slug,])
	if cursor.rowcount == 0:
		cursor.close()
		return JsonResponse({}, status = 404)
	limit = 99999999
	if 'limit' in request.GET:
		limit = request.GET['limit']
	order = False
	if 'desc' in request.GET:
		order = True if request.GET['desc'] == 'true' else False
	since = ' '
	if 'since' in request.GET:
		since = request.GET['since']
	if order:
		if 'since' not in request.GET:
			since = 'ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'
		cursor.execute(SELECT_USERS_BY_FORUM_DESC, [since, forum_slug, forum_slug, limit])
	else:
		cursor.execute(SELECT_USERS_BY_FORUM_ASC, [since, forum_slug, forum_slug, limit])
	param_array = ["about", "email", "fullname", "nickname"]
	users = [dict(zip(param_array, user)) for user in cursor.fetchall()]
	cursor.close()
	return JsonResponse(users, status = 200, safe = False)